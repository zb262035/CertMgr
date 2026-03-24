"""Certificate CRUD routes."""
import os
from flask import render_template, redirect, url_for, flash, send_file, abort, request, current_app
from flask_login import login_required, current_user
from app.extensions import db
from app.models.certificate import Certificate
from app.models.user import User
from app.blueprints.certificates import certificates_bp
from app.blueprints.certificates.forms import CertificateBaseForm, CertificateEditForm, FIELD_SCHEMAS
from app.blueprints.certificates.services import CertificateService, ExcelImportService
from app.decorators import admin_required


@certificates_bp.route('/')
@login_required
def list():
    """List user's certificates (card layout)."""
    if current_user.is_admin:
        certificates = Certificate.query.order_by(Certificate.created_at.desc()).all()
    else:
        certificates = Certificate.query.filter_by(user_id=current_user.id).order_by(Certificate.created_at.desc()).all()
    return render_template('certificates/list.html', certificates=certificates)


@certificates_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """Upload new certificate with dynamic fields (same-page switching)."""
    form = CertificateBaseForm()
    if form.validate_on_submit():
        try:
            import json
            dynamic_fields_json = request.form.get('dynamic_fields_json', '{}')
            dynamic_fields = json.loads(dynamic_fields_json) if dynamic_fields_json else {}

            certificate = CertificateService.create_certificate(
                user_id=current_user.id,
                title=form.title.data,
                certificate_type_id=form.certificate_type_id.data,
                file=form.file.data,
                dynamic_fields=dynamic_fields
            )
            flash('证书上传成功 / Certificate uploaded successfully.', 'success')
            return redirect(url_for('certificates.detail', cert_id=certificate.id))
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash(f'上传失败 / Upload failed: {str(e)}', 'danger')

    return render_template('certificates/upload.html', form=form, FIELD_SCHEMAS=FIELD_SCHEMAS)


@certificates_bp.route('/<int:cert_id>')
@login_required
def detail(cert_id):
    """View certificate detail (edit/delete from here per user decision)."""
    certificate = Certificate.query.get_or_404(cert_id)
    if not current_user.is_admin and certificate.user_id != current_user.id:
        abort(403)
    return render_template('certificates/detail.html', certificate=certificate)


@certificates_bp.route('/<int:cert_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(cert_id):
    """Edit certificate."""
    certificate = Certificate.query.get_or_404(cert_id)
    if not current_user.is_admin and certificate.user_id != current_user.id:
        abort(403)

    form = CertificateEditForm()

    if form.validate_on_submit():
        try:
            import json
            dynamic_fields_json = request.form.get('dynamic_fields_json', '{}')
            dynamic_fields = json.loads(dynamic_fields_json) if dynamic_fields_json else {}

            CertificateService.update_certificate(
                certificate=certificate,
                title=form.title.data,
                certificate_type_id=form.certificate_type_id.data,
                file=form.file.data if form.file.data else None,
                dynamic_fields=dynamic_fields
            )
            flash('证书更新成功 / Certificate updated successfully.', 'success')
            return redirect(url_for('certificates.detail', cert_id=certificate.id))
        except Exception as e:
            flash(f'更新失败 / Update failed: {str(e)}', 'danger')

    if request.method == 'GET':
        form.title.data = certificate.title
        form.certificate_type_id.data = certificate.certificate_type_id

    return render_template('certificates/edit.html', form=form, certificate=certificate, FIELD_SCHEMAS=FIELD_SCHEMAS)


@certificates_bp.route('/<int:cert_id>/delete', methods=['POST'])
@login_required
def delete(cert_id):
    """Delete certificate."""
    certificate = Certificate.query.get_or_404(cert_id)
    if not current_user.is_admin and certificate.user_id != current_user.id:
        abort(403)

    try:
        CertificateService.delete_certificate(certificate)
        flash('证书已删除 / Certificate deleted.', 'success')
    except Exception as e:
        flash(f'删除失败 / Delete failed: {str(e)}', 'danger')

    return redirect(url_for('certificates.list'))


@certificates_bp.route('/<int:cert_id>/file')
@login_required
def file(cert_id):
    """Serve certificate file."""
    certificate = Certificate.query.get_or_404(cert_id)
    if not current_user.is_admin and certificate.user_id != current_user.id:
        abort(403)

    file_full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], certificate.file_path)
    return send_file(file_full_path, mimetype=certificate.file_mime_type)


@certificates_bp.route('/ocr/upload', methods=['GET', 'POST'])
@login_required
def ocr_upload():
    """OCR upload page - accepts certificate image/PDF, runs OCR, shows confirmation."""
    if request.method == 'GET':
        return render_template('certificates/ocr_upload.html')

    # Handle file upload
    if 'file' not in request.files:
        flash('请选择文件 / Please select a file', 'danger')
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        flash('请选择文件 / Please select a file', 'danger')
        return redirect(request.url)

    # Validate file type
    allowed = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in allowed:
        flash('不支持的文件格式 / Unsupported file format', 'danger')
        return redirect(request.url)

    try:
        # Save file temporarily for OCR
        import uuid
        temp_filename = f'ocr_temp_{uuid.uuid4().hex}.{ext}'
        temp_path = os.path.join(current_app.config['UPLOAD_FOLDER'], temp_filename)
        file.save(temp_path)

        # Run OCR
        from app.services.ocr_service import OCRService
        result = OCRService.recognize_certificate(
            temp_path,
            file.content_type or f'application/{ext}'
        )

        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

        if not result['success']:
            flash(result.get('error', 'OCR识别失败 / OCR recognition failed'), 'danger')
            return redirect(request.url)

        # Store OCR result in session for confirmation
        import json
        session['ocr_result'] = {
            'type': result['type'],
            'title': result['title'],
            'fields': result['fields'],
            'file_mime_type': file.content_type,
            'filename': file.filename,
        }

        return render_template('certificates/ocr_confirm.html',
                               ocr_result=result,
                               filename=file.filename,
                               FIELD_SCHEMAS=FIELD_SCHEMAS)

    except Exception as e:
        flash(f'处理失败 / Processing failed: {str(e)}', 'danger')
        return redirect(url_for('certificates.ocr_upload'))


@certificates_bp.route('/ocr/confirm', methods=['POST'])
@login_required
def ocr_confirm():
    """Confirm OCR results and save certificate."""
    import json

    ocr_result = session.get('ocr_result')
    if not ocr_result:
        flash('会话过期，请重新上传 / Session expired, please upload again', 'warning')
        return redirect(url_for('certificates.ocr_upload'))

    try:
        # Get form data
        title = request.form.get('title')
        cert_type_name = request.form.get('certificate_type')
        dynamic_fields_json = request.form.get('dynamic_fields_json', '{}')
        dynamic_fields = json.loads(dynamic_fields_json) if dynamic_fields_json else {}

        # Find certificate type
        from app.models.certificate import CertificateType
        cert_type = CertificateType.query.filter_by(name=cert_type_name).first()
        if not cert_type:
            flash('未找到证书类型 / Certificate type not found', 'danger')
            return redirect(url_for('certificates.ocr_upload'))

        # Create certificate (no file for OCR flow - file_path will be empty)
        certificate = Certificate(
            user_id=current_user.id,
            title=title,
            certificate_type_id=cert_type.id,
            file_path='',  # OCR flow doesn't store file yet
            original_filename=ocr_result.get('filename', ''),
            file_mime_type=ocr_result.get('file_mime_type', ''),
            fields=dynamic_fields
        )
        db.session.add(certificate)
        db.session.commit()

        # Clear session
        session.pop('ocr_result', None)

        flash('证书创建成功 / Certificate created successfully', 'success')
        return redirect(url_for('certificates.detail', cert_id=certificate.id))

    except Exception as e:
        flash(f'创建失败 / Creation failed: {str(e)}', 'danger')
        return redirect(url_for('certificates.ocr_upload'))


@certificates_bp.route('/import', methods=['GET', 'POST'])
@login_required
@admin_required
def import_batch():
    """Batch import certificates from Excel file (admin only).

    Auto-parse without template per user decision.
    """
    if request.method == 'GET':
        users = User.query.order_by(User.email).all()
        return render_template('certificates/import.html', users=users)

    if 'file' not in request.files:
        flash('请选择文件 / Please select a file', 'danger')
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        flash('请选择文件 / Please select a file', 'danger')
        return redirect(request.url)

    if not file.filename.endswith(('.xlsx', '.xls')):
        flash('请上传 Excel 文件 / Please upload an Excel file', 'danger')
        return redirect(request.url)

    try:
        # Parse Excel
        records, parse_errors = ExcelImportService.parse_excel(file)

        if parse_errors:
            for error in parse_errors:
                flash(error, 'warning')

        if not records:
            flash('未能从文件中解析出证书记录 / No certificate records parsed from file', 'warning')
            return redirect(request.url)

        # Import records
        # Get user_id from form dropdown (required field)
        target_user_id = request.form.get('user_id', type=int)
        if not target_user_id:
            flash('请选择目标用户 / Please select target user', 'danger')
            return redirect(request.url)
        success_count, import_errors = ExcelImportService.import_batch(records, user_id=target_user_id)

        flash(f'成功导入 {success_count} 个证书 / Successfully imported {success_count} certificates', 'success')

        if import_errors:
            for error in import_errors:
                flash(error, 'danger')

        return redirect(url_for('certificates.list'))

    except Exception as e:
        flash(f'导入失败 / Import failed: {str(e)}', 'danger')
        return redirect(request.url)

