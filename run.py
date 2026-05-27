import sys
import os

# Put src/ into search path to load modules correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from app import app

if __name__ == '__main__':
    print("====================================================")
    print("  Starting Flask Service Dashboard on port 19191")
    print("  Access dashboard at: http://localhost:19191/")
    print("====================================================")
    
    # Run the server on host 0.0.0.0 and port 19191
    app.run(host='0.0.0.0', port=19191, debug=True)
