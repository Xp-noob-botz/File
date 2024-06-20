from flask import Flask, request, send_from_directory, redirect, url_for, render_template_string, session
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Replace with a real secret key in production
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

PASSWORD = 'ashu@'

login_form = '''
<!doctype html>
<title>Login</title>
<h1>Please enter the password</h1>
<form method=post>
  <input type=password name=password>
  <input type=submit value=Login>
</form>
'''

file_manager_template = '''
<!doctype html>
<title>File Manager</title>
<h1>Upload new Files</h1>
<form id="uploadForm" method="post" enctype="multipart/form-data" action="/upload">
  <input type="file" name="files" multiple>
  <input type="submit" value="Upload">
  <progress id="progressBar" value="0" max="100" style="width:100%;"></progress>
</form>
<div id="status"></div>

<h1>Files</h1>
<ul>
  {% for file in files %}
  <li><a href="/download/{{ file }}">{{ file }}</a></li>
  {% endfor %}
</ul>
<a href="/logout">Logout</a>

<script>
document.getElementById('uploadForm').addEventListener('submit', function(e) {
  var files = document.querySelector('[type=file]').files;
  var progressBar = document.getElementById('progressBar');
  var status = document.getElementById('status');
  
  var formData = new FormData();
  
  for (var i = 0; i < files.length; i++) {
    formData.append('files', files[i]);
  }
  
  var xhr = new XMLHttpRequest();
  
  xhr.upload.addEventListener('progress', function(e) {
    if (e.lengthComputable) {
      var percent = Math.round((e.loaded / e.total) * 100);
      progressBar.value = percent;
      status.innerText = 'Uploading... ' + percent + '%';
    }
  });
  
  xhr.upload.addEventListener('load', function(e) {
    progressBar.value = 0;
    status.innerText = 'Upload complete.';
    setTimeout(function() {
      status.innerText = '';
    }, 2000); // Clear status after 2 seconds
  });
  
  xhr.open('POST', '/upload');
  xhr.send(formData);
  
  e.preventDefault();
});
</script>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'logged_in' in session:
        files = os.listdir(app.config['UPLOAD_FOLDER'])
        return render_template_string(file_manager_template, files=files)
    if request.method == 'POST':
        password = request.form.get('password')
        if password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template_string(login_form) + '<p style="color:red;">Incorrect password, please try again.</p>'
    return render_template_string(login_form)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'logged_in' in session:
        if 'files' not in request.files:
            return redirect(request.url)
        
        uploaded_files = request.files.getlist('files')
        file_count = len(uploaded_files)
        uploaded_count = 0
        
        for file in uploaded_files:
            if file.filename == '':
                continue
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            uploaded_count += 1
            
            # Calculate progress percentage
            progress_percent = int((uploaded_count / file_count) * 100)
            print(f"File {uploaded_count}/{file_count} uploaded ({progress_percent}% complete)")

        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_file(filename):
    if 'logged_in' in session:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    else:
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
