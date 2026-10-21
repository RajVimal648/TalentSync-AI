import os
import json
from flask import Flask, render_template, request, jsonify, session
from werkzeug.utils import secure_filename

import database
import resume_engine

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'talentsync-ai-secret-key-2026')

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max limit

# Ensure database tables exist
database.init_db()

@app.route('/')
def index():
    user = None
    if 'user_id' in session:
        user = database.get_user_by_id(session['user_id'])
    roles = database.get_all_job_roles()
    presets = {r['role_title']: r['description'] for r in roles}
    for k, v in resume_engine.ROLE_PRESETS.items():
        if k not in presets:
            presets[k] = v
    return render_template('index.html', user=user, role_presets=presets, job_roles=roles)

@app.route('/api/roles', methods=['GET', 'POST'])
def handle_roles():
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        role_title = data.get('role_title', '').strip()
        description = data.get('description', '').strip()
        required_skills = data.get('required_skills', '').strip()

        if not role_title or not description:
            return jsonify({'success': False, 'error': 'Role title and description are required.'}), 400

        saved = database.save_or_update_job_role(role_title, description, required_skills)
        return jsonify({'success': True, 'role': saved})

    # GET: return all roles stored in the database
    roles = database.get_all_job_roles()
    presets = {r['role_title']: r['description'] for r in roles}
    for k, v in resume_engine.ROLE_PRESETS.items():
        if k not in presets:
            presets[k] = v

    return jsonify({
        'success': True,
        'roles': roles,
        'presets': presets,
        'taxonomy': resume_engine.TECH_SKILLS_TAXONOMY
    })

@app.route('/api/upload-pdf', methods=['POST'])
def upload_pdf():
    if 'pdf' not in request.files:
        return jsonify({'success': False, 'error': 'No file part in request'}), 400
    
    file = request.files['pdf']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400

    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'success': False, 'error': 'File must be a PDF document (.pdf)'}), 400

    try:
        filename = secure_filename(file.filename)
        # Extract text directly from stream without requiring saving first
        extracted_text = resume_engine.extract_text_from_pdf(file.stream)
        if not extracted_text.strip():
            return jsonify({
                'success': False, 
                'error': 'Could not extract readable text from PDF. It may be an image scan or password protected.'
            }), 422

        return jsonify({
            'success': True,
            'filename': filename,
            'text': extracted_text
        })
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to process PDF: {str(e)}'}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json(silent=True) or {}
        
        # Also support multipart/form-data
        if not data and request.form:
            data = request.form.to_dict()

        resume_text = data.get('resume_text', '')
        job_description = data.get('job_description', '')
        target_role = data.get('target_role', 'Software Developer')
        filename = data.get('filename', 'resume_upload.pdf')

        # If a PDF file was uploaded in this request directly
        if 'resume_pdf' in request.files:
            file = request.files['resume_pdf']
            if file and file.filename.lower().endswith('.pdf'):
                filename = secure_filename(file.filename)
                extracted = resume_engine.extract_text_from_pdf(file.stream)
                if extracted.strip():
                    resume_text = extracted

        if not resume_text.strip():
            return jsonify({'success': False, 'error': 'Resume text is required.'}), 400
        if not job_description.strip():
            return jsonify({'success': False, 'error': 'Job description is required.'}), 400

        result = resume_engine.analyze_resume(
            resume_text=resume_text,
            job_description=job_description,
            target_role=target_role
        )

        user_id = session.get('user_id')
        analysis_id = database.save_analysis(
            user_id=user_id,
            resume_filename=filename,
            resume_text=resume_text,
            target_role=result['target_role'],
            match_score=result['final_score'],
            tfidf_score=result['tfidf_score'],
            section_score=result['section_score'],
            detected_skills=result['detected_skills'],
            missing_skills=result['missing_skills']
        )
        result['analysis_id'] = analysis_id
        result['success'] = True

        # Save or update job role and JD in the database so that roles and JDs are continuously defined and updated in the DB
        try:
            database.save_or_update_job_role(target_role, job_description)
        except Exception as e:
            app.logger.warning(f"Could not auto-save job role to database: {e}")

        return jsonify(result)

    except ValueError as val_err:
        return jsonify({'success': False, 'error': str(val_err)}), 400
    except Exception as e:
        app.logger.error(f"Analysis error: {e}")
        return jsonify({'success': False, 'error': f'Analysis error: {str(e)}'}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    user_id = session.get('user_id')
    history = database.get_analysis_history(user_id=user_id)
    return jsonify({'success': True, 'history': history})

@app.route('/api/history/<int:analysis_id>', methods=['DELETE'])
def delete_history_item(analysis_id):
    user_id = session.get('user_id')
    database.delete_analysis(analysis_id, user_id=user_id)
    return jsonify({'success': True, 'message': 'Analysis deleted.'})

@app.route('/api/history', methods=['DELETE'])
def clear_history():
    user_id = session.get('user_id')
    database.clear_all_history(user_id=user_id)
    return jsonify({'success': True, 'message': 'Scan history cleared.'})

# --- Authentication Endpoints ---

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    full_name = data.get('full_name', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    if not full_name or not email or not password:
        return jsonify({'success': False, 'error': 'Please provide full name, email, and password.'}), 400

    res = database.register_user(full_name, email, password)
    if res['success']:
        session['user_id'] = res['user']['user_id']
        return jsonify(res)
    else:
        return jsonify(res), 400

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    if not email or not password:
        return jsonify({'success': False, 'error': 'Please provide email and password.'}), 400

    res = database.authenticate_user(email, password)
    if res['success']:
        session['user_id'] = res['user']['user_id']
        return jsonify(res)
    else:
        return jsonify(res), 401

@app.route('/api/auth/logout', methods=['POST', 'GET'])
def logout():
    session.pop('user_id', None)
    return jsonify({'success': True, 'message': 'Logged out successfully.'})

@app.route('/api/auth/current-user', methods=['GET'])
def current_user():
    if 'user_id' in session:
        user = database.get_user_by_id(session['user_id'])
        if user:
            return jsonify({'success': True, 'user': user})
    return jsonify({'success': True, 'user': None})

@app.errorhandler(413)
def file_too_large(e):
    return jsonify({'success': False, 'error': 'Uploaded file exceeds 16 MB maximum size.'}), 413

@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'error': 'API route not found'}), 404
    return render_template('index.html'), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # use_reloader=False prevents 'signal only works in main thread' error in Python 3.14/Windows
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)

