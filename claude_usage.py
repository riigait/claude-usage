"""
Claude Usage — combined entry point.

Run without arguments to open the desktop widget.
Run with --check to execute the terminal checker (used by the widget subprocess).
"""

import sys

if "--check" in sys.argv[1:]:
    from check_usage import main
    sys.exit(main())
else:
    from widget import ClaudeWidget
    app = ClaudeWidget()
    app.mainloop()
