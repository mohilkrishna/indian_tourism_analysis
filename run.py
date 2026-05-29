#!/usr/bin/env python
import sys

def main():
    
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\n Server stopped")
        sys.exit(0)

if __name__ == '__main__':
    main()