import random
import subprocess
from flask import jsonify, render_template
from flask import Flask, render_template, request
import joblib
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# Load the trained model
model_path = "cpu_prediction_model.pkl"
model = joblib.load(model_path)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/statistics')
def statistics():
    # Add logic to fetch and display statistics
    return render_template('statistics.html')

@app.route('/predictions', methods=['GET', 'POST'])
def predictions():
    if request.method == 'POST':
        # Get input data from the form
        memory_usage = float(request.form.get('memory_usage'))
        disk_write_bytes = float(request.form.get('disk_write_bytes'))
        network_sent_bytes = float(request.form.get('network_sent_bytes'))
        system_cpu_usage = float(request.form.get('system_cpu_usage'))
        system_memory_usage = float(request.form.get('system_memory_usage'))
        system_disk_write_bytes = float(request.form.get('system_disk_write_bytes'))
        system_network_sent_bytes = float(request.form.get('system_network_sent_bytes'))
        
        # Perform any necessary data preprocessing
        input_data = [[memory_usage, disk_write_bytes, network_sent_bytes, system_cpu_usage, 
                       system_memory_usage, system_disk_write_bytes, system_network_sent_bytes]]
        
        # Use the model to make predictions
        predicted_cpu_usage = model.predict(input_data)[0]
        
        # Return predictions to the user
        return render_template('predictions.html', predicted_cpu_usage=predicted_cpu_usage)
    else:
        # Render the form template for GET requests
        return render_template('form.html')
    
@app.route('/get_system_metrics', methods=['GET'])
def get_system_metrics():
    # Code to collect system metrics (simplified)
    # You need to replace this with your actual system metrics collection code
    output = subprocess.check_output(['your_command_to_collect_metrics'])
    return output

@app.route('/allocation', methods=['GET', 'POST'])
def allocation():
    if request.method == 'POST':
        process_name = request.form.get('process_name')
        priority_class = request.form.get('priority_class')

        # Mapping of priority class names to integer values
        priority_map = {
            "AboveNormal": 32768,
            "BelowNormal": 16384,
            "High": 128,
            "Normal": 32,
            "RealTime": 256
        }

        # Get the corresponding integer priority value from the map
        priority_value = priority_map.get(priority_class, 32)  # Default to Normal if priority class not found

        # Generate PowerShell script
        script = f"$processName = '{process_name}'\n"
        script += f"$priorityClass = {priority_value}\n"  # Use the integer priority value
        script += "Get-WmiObject Win32_Process | Where-Object {$_.Name -eq $processName} | ForEach-Object {\n"
        script += "$_.SetPriority($priorityClass)\n}\n"

        # Execute PowerShell script
        try:
            subprocess.run(["powershell", "-Command", script], check=True)
            message = f"Priority for process '{process_name}' set to '{priority_class}' successfully."
        except subprocess.CalledProcessError as e:
            message = f"Error occurred while setting priority for process '{process_name}': {e}"

        return render_template('allocation_result.html', message=message)
    else:
        # Render the form template for GET requests
        return render_template('allocation.html')

def generate_data():
    cpu_utilization = random.randint(0, 100)
    memory_utilization = random.randint(0, 100)
    disk_utilization = random.randint(0, 100)
    network_utilization = random.randint(0, 100)
    return cpu_utilization, memory_utilization, disk_utilization, network_utilization


# Route to fetch real-time data
@app.route('/realtime_data')
def realtime_data():
    cpu, memory, disk, network = generate_data()
    # Restructure data for Plotly
    data = [{'resource': 'CPU', 'usage': cpu},
            {'resource': 'Memory', 'usage': memory},
            {'resource': 'Disk', 'usage': disk},
            {'resource': 'Network', 'usage': network}]
    return jsonify(data)


# Route to render HTML page with real-time plot
@app.route('/realtime_stats')
def realtime_stats():
    return render_template('real-time.html')

if __name__ == '__main__':
    app.run(debug=True)
