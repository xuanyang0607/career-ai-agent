#!/usr/bin/env python3
"""
Basic test script to check if the web interface can start
This version works without OpenAI API key and spaCy model
"""

try:
    from flask import Flask, render_template_string
    
    app = Flask(__name__)
    
    # Simple HTML template for testing
    test_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Career AI Agent - Test</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
            .header { text-align: center; color: #333; margin-bottom: 30px; }
            .test-section { background: #e8f4f8; padding: 20px; margin: 20px 0; border-radius: 8px; }
            .success { color: #28a745; font-weight: bold; }
            .info { color: #17a2b8; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Career AI Agent - Basic Test</h1>
                <p>Testing if the web interface can start...</p>
            </div>
            
            <div class="test-section">
                <h3 class="success">✅ Web Interface is Working!</h3>
                <p class="info">Flask is running successfully. This confirms that the basic web framework is functional.</p>
            </div>
            
            <div class="test-section">
                <h3>Next Steps:</h3>
                <ol>
                    <li><strong>Install Developer Tools:</strong> Run <code>xcode-select --install</code></li>
                    <li><strong>Install Dependencies:</strong> Run <code>pip3 install -r requirements.txt</code></li>
                    <li><strong>Download spaCy Model:</strong> Run <code>python3 -m spacy download en_core_web_sm</code></li>
                    <li><strong>Add OpenAI API Key:</strong> Edit the <code>.env</code> file</li>
                    <li><strong>Run Full Interface:</strong> Run <code>python3 run_web.py</code></li>
                </ol>
            </div>
            
            <div class="test-section">
                <h3>What's Working:</h3>
                <ul>
                    <li>✅ Python is functional</li>
                    <li>✅ Flask web framework</li>
                    <li>✅ HTML rendering</li>
                    <li>✅ Basic styling</li>
                </ul>
            </div>
            
            <div class="test-section">
                <h3>Still Needed:</h3>
                <ul>
                    <li>⏳ Developer tools installation</li>
                    <li>⏳ Python dependencies</li>
                    <li>⏳ spaCy NLP model</li>
                    <li>⏳ OpenAI API key (for AI features)</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """
    
    @app.route('/')
    def test_page():
        return render_template_string(test_template)
    
    if __name__ == '__main__':
        print("🧪 Starting basic test server...")
        print("📱 Open your browser and go to: http://localhost:5001")
        print("🔧 Press Ctrl+C to stop")
        print("=" * 50)
        app.run(debug=True, host='0.0.0.0', port=5001)
        
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("You need to install Flask first.")
    print("Try: pip3 install flask")
except Exception as e:
    print(f"❌ Error: {e}")
