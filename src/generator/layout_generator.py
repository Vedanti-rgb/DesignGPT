import json

# Placeholder HTML template with Jinja-like variables for substitution
MINIMAL_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DesignGPT UI Preview</title>
    <style>
        /* Global Styles based on AI Spec */
        body {
            background-color: {{BG_COLOR}};
            color: {{TEXT_COLOR}};
            font-family: {{BODY_FONT}};
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
        }
        .container {
            background-color: {{CARD_COLOR}};
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
            width: 100%;
            max-width: 400px;
            text-align: center;
        }
        h2 {
            color: {{PRIMARY_COLOR}};
            font-family: {{HEADER_FONT}};
            margin-bottom: 20px;
        }
        .input-field {
            width: 90%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ccc;
            border-radius: 6px;
            box-sizing: border-box;
        }
        .main-button {
            background-color: {{PRIMARY_COLOR}};
            color: white;
            padding: 12px 20px;
            margin-top: 20px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            width: 100%;
            font-size: 16px;
            transition: background-color 0.3s;
        }
        .main-button:hover {
            background-color: {{ACCENT_COLOR}};
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>{{PAGE_TYPE}}</h2>
        <input type="text" class="input-field" placeholder="Username or Email">
        <input type="password" class="input-field" placeholder="Password">
        <button class="main-button">
            {{PAGE_TYPE.split()[0]}}
        </button>
        <p style="margin-top: 15px; font-size: 12px;">{{RATIONALE}}</p>
    </div>
</body>
</html>
"""

def generate_html_ui(design_spec: dict) -> str:
    """
    Takes the design specification dictionary and substitutes values into the HTML template.
    """
    # Defensive programming: Use safe defaults for colors if AI misses them
    colors = design_spec.get('color_palette', ["#2c3e50", "#e74c3c", "#ecf0f1"])
    
    # Assign colors to logical variables
    primary_color = colors[0] if len(colors) > 0 else "#2c3e50"
    accent_color = colors[1] if len(colors) > 1 else "#e74c3c"
    bg_color = colors[2] if len(colors) > 2 else "#ecf0f1"

    # Determine text color based on background (simple contrast logic)
    # If the BG is dark (first two hex chars less than '50' is a proxy), use white text.
    if int(bg_color[1:3], 16) < 100:
        text_color = "#FFFFFF"
    else:
        text_color = "#333333" # Dark text

    # Assign fonts
    fonts = design_spec.get('fonts', {"header": "Arial, sans-serif", "body": "Helvetica, sans-serif"})

    # Start with the base template
    html_content = MINIMAL_TEMPLATE

    # Substitution mapping
    substitutions = {
        '{{PRIMARY_COLOR}}': primary_color,
        '{{ACCENT_COLOR}}': accent_color,
        '{{BG_COLOR}}': bg_color,
        '{{CARD_COLOR}}': design_spec.get('style', 'minimalist') == 'dark' and primary_color or '#FFFFFF',
        '{{TEXT_COLOR}}': text_color,
        '{{HEADER_FONT}}': fonts.get('header', 'Arial, sans-serif'),
        '{{BODY_FONT}}': fonts.get('body', 'Helvetica, sans-serif'),
        '{{PAGE_TYPE}}': design_spec.get('page_type', 'Default Form'),
        '{{RATIONALE}}': design_spec.get('rationale', 'Design rationale not provided.')
    }
    
    # Perform substitutions
    for placeholder, value in substitutions.items():
        html_content = html_content.replace(placeholder, str(value))
        
    return html_content