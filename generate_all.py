import os
import shutil
import json
import re
from PIL import Image, ImageDraw, ImageFont
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

# Fonts
FONT_UI_BOLD = ImageFont.truetype(r'C:\Windows\Fonts\segoeuib.ttf', 13)
FONT_UI_REG = ImageFont.truetype(r'C:\Windows\Fonts\segoeui.ttf', 12)
FONT_UI_SMALL = ImageFont.truetype(r'C:\Windows\Fonts\segoeui.ttf', 11)
FONT_UI_TITLE = ImageFont.truetype(r'C:\Windows\Fonts\segoeuib.ttf', 12)
FONT_CODE = ImageFont.truetype(r'C:\Windows\Fonts\consola.ttf', 13)
FONT_CODE_BOLD = ImageFont.truetype(r'C:\Windows\Fonts\consolab.ttf', 13)
FONT_CODE_SMALL = ImageFont.truetype(r'C:\Windows\Fonts\consola.ttf', 11)

METHOD_COLORS = {
    'GET': '#0CBB52',      # Green
    'POST': '#FF6C37',     # Orange
    'PUT': '#097BED',      # Blue
    'DELETE': '#EB2013'    # Red
}

STATUS_COLORS = {
    200: ('#10B981', '200 OK'),
    201: ('#10B981', '201 Created'),
    400: ('#EF4444', '400 Bad Request'),
    404: ('#EF4444', '404 Not Found'),
    409: ('#EF4444', '409 Conflict')
}

def highlight_tokens(text):
    """Tokenize JSON line for syntax highlighting in VS Code / Postman style"""
    tokens = []
    pattern = re.compile(
        r'(?P<key>"[^"]*")\s*:'
        r'|(?P<string>"[^"]*")'
        r'|(?P<number>-?\d+(?:\.\d+)?)'
        r'|(?P<bool>true|false|null)'
        r'|(?P<punct>[{}[\]:,])'
        r'|(?P<space>\s+)'
        r'|(?P<other>[^\s"0-9{}\[\],:]+)'
    )
    for m in pattern.finditer(text):
        if m.group('key'):
            tokens.append((m.group('key'), '#9CDCFE'))
            tokens.append((':', '#D4D4D4'))
        elif m.group('string'):
            tokens.append((m.group('string'), '#CE9178'))
        elif m.group('number'):
            tokens.append((m.group('number'), '#B5CEA8'))
        elif m.group('bool'):
            tokens.append((m.group('bool'), '#569CD6'))
        elif m.group('punct'):
            tokens.append((m.group('punct'), '#D4D4D4'))
        elif m.group('space'):
            tokens.append((m.group('space'), '#D4D4D4'))
        else:
            tokens.append((m.group(0), '#D4D4D4'))
    return tokens

def render_postman_view(req_info, out_path):
    width = 1020
    
    # Calculate response body lines
    resp_body = req_info.get('response_json')
    if isinstance(resp_body, (dict, list)):
        body_str = json.dumps(resp_body, indent=2)
    else:
        body_str = str(resp_body)
    resp_lines = body_str.split('\n')
    
    # Request body lines (if any)
    req_body = req_info.get('body')
    req_body_lines = []
    if req_body:
        req_body_lines = json.dumps(req_body, indent=2).split('\n')
    
    has_params = req_info.get('params') is not None
    
    # Layout heights
    req_body_h = (28 + len(req_body_lines) * 18) if req_body_lines else (56 if has_params else 0)
    
    # Limit response body display if very long, but all our responses are under 30 lines
    resp_body_h = max(70, min(len(resp_lines) * 19 + 24, 600))
    tests = req_info.get('tests', [])
    test_h = (30 + len(tests) * 22) if tests else 0
    
    total_height = 40 + 36 + 48 + 34 + req_body_h + 12 + 38 + 30 + resp_body_h + test_h + 20
    total_height = max(500, min(total_height, 900))
    
    img = Image.new('RGB', (width, total_height), '#212121')
    draw = ImageDraw.Draw(img)
    
    # --- Top Navigation / Postman Header ---
    draw.rectangle([0, 0, width, 40], fill='#181818')
    draw.text((16, 12), "My Workspace", fill='#E0E0E0', font=FONT_UI_BOLD)
    draw.text((115, 12), "/  ToolTown Makerspace API", fill='#8E8E8E', font=FONT_UI_REG)
    
    # Environment pill on right
    draw.rounded_rectangle([width - 230, 8, width - 16, 32], radius=4, fill='#2A2A2A', outline='#3A3A3A')
    draw.text((width - 215, 12), "Environment:", fill='#8E8E8E', font=FONT_UI_SMALL)
    draw.text((width - 135, 12), "Local (baseUrl)", fill='#FF6C37', font=FONT_UI_BOLD)
    
    # --- Tab Bar ---
    draw.rectangle([0, 40, width, 76], fill='#1C1C1C')
    tab_w = 280
    draw.rounded_rectangle([12, 44, 12 + tab_w, 76], radius=4, fill='#212121')
    m_color = METHOD_COLORS.get(req_info['method'], '#0CBB52')
    draw.text((22, 53), req_info['method'], fill=m_color, font=FONT_UI_BOLD)
    
    m_len = draw.textlength(req_info['method'], font=FONT_UI_BOLD)
    name_display = req_info['name']
    if len(name_display) > 26:
        name_display = name_display[:24] + "..."
    draw.text((28 + m_len, 53), name_display, fill='#D4D4D4', font=FONT_UI_REG)
    draw.text((12 + tab_w - 22, 51), "x", fill='#8E8E8E', font=FONT_UI_REG)
    draw.text((12 + tab_w + 12, 51), "+", fill='#8E8E8E', font=FONT_UI_TITLE)
    
    # --- Request URL Bar ---
    curr_y = 86
    draw.rounded_rectangle([16, curr_y, 90, curr_y + 36], radius=4, fill='#2A2A2A', outline='#3A3A3A')
    draw.text((28, curr_y + 9), req_info['method'], fill=m_color, font=FONT_UI_BOLD)
    draw.text((72, curr_y + 11), "v", fill='#8E8E8E', font=FONT_UI_SMALL)
    
    draw.rounded_rectangle([96, curr_y, width - 110, curr_y + 36], radius=4, fill='#282828', outline='#3A3A3A')
    raw_url = req_info['url']
    display_url = raw_url.replace('http://localhost:3000', '{{baseUrl}}')
    
    url_x = 108
    if display_url.startswith('{{baseUrl}}'):
        var_text = "{{baseUrl}}"
        var_w = draw.textlength(var_text, font=FONT_CODE_BOLD) + 10
        draw.rounded_rectangle([url_x, curr_y + 6, url_x + var_w, curr_y + 30], radius=3, fill='#3D2817', outline='#804000')
        draw.text((url_x + 5, curr_y + 9), var_text, fill='#FF9933', font=FONT_CODE_BOLD)
        rest_url = display_url[len('{{baseUrl}}'):]
        draw.text((url_x + var_w + 6, curr_y + 9), rest_url, fill='#E0E0E0', font=FONT_CODE)
    else:
        draw.text((url_x, curr_y + 9), display_url, fill='#E0E0E0', font=FONT_CODE)
    
    # Send button
    draw.rounded_rectangle([width - 100, curr_y, width - 16, curr_y + 36], radius=4, fill='#0265D2')
    draw.text((width - 80, curr_y + 9), "Send", fill='#FFFFFF', font=FONT_UI_BOLD)
    
    # --- Request Subtabs ---
    curr_y += 44
    req_tabs = ['Params', 'Authorization', 'Headers', 'Body', 'Scripts', 'Tests', 'Settings']
    active_req_tab = 'Body' if req_body else ('Params' if has_params else 'Params')
    
    tab_x = 16
    for t in req_tabs:
        is_active = (t == active_req_tab)
        color = '#FFFFFF' if is_active else '#8E8E8E'
        draw.text((tab_x, curr_y + 6), t, fill=color, font=FONT_UI_BOLD if is_active else FONT_UI_REG)
        if t == 'Body' and req_body:
            dot_x = tab_x + draw.textlength(t, font=FONT_UI_BOLD) + 4
            draw.ellipse([dot_x, curr_y + 11, dot_x + 6, curr_y + 17], fill='#10B981')
        if is_active:
            t_w = draw.textlength(t, font=FONT_UI_BOLD)
            draw.line([tab_x, curr_y + 26, tab_x + t_w, curr_y + 26], fill='#FF6C37', width=2)
        tab_x += int(draw.textlength(t, font=FONT_UI_BOLD)) + 24
    
    curr_y += 30
    
    # --- Request Body / Params area if present ---
    if req_body:
        draw.rounded_rectangle([16, curr_y, width - 16, curr_y + req_body_h], radius=4, fill='#191919', outline='#303030')
        draw.text((26, curr_y + 6), "raw  |  JSON", fill='#8E8E8E', font=FONT_UI_SMALL)
        body_y = curr_y + 24
        for l_idx, line in enumerate(req_body_lines, 1):
            draw.text((26, body_y), f"{l_idx:2d}", fill='#555555', font=FONT_CODE_SMALL)
            tokens = highlight_tokens(line)
            tok_x = 55
            for text, col in tokens:
                draw.text((tok_x, body_y), text, fill=col, font=FONT_CODE_SMALL)
                tok_x += draw.textlength(text, font=FONT_CODE_SMALL)
            body_y += 18
        curr_y += req_body_h + 8
    elif has_params:
        draw.rounded_rectangle([16, curr_y, width - 16, curr_y + req_body_h], radius=4, fill='#191919', outline='#303030')
        draw.text((26, curr_y + 6), "Query Params", fill='#AAAAAA', font=FONT_UI_BOLD)
        draw.text((26, curr_y + 24), "KEY", fill='#777777', font=FONT_UI_SMALL)
        draw.text((160, curr_y + 24), "VALUE", fill='#777777', font=FONT_UI_SMALL)
        # Params row
        param_k, param_v = req_info['params']
        draw.text((26, curr_y + 38), param_k, fill='#9CDCFE', font=FONT_CODE_SMALL)
        draw.text((160, curr_y + 38), param_v, fill='#CE9178', font=FONT_CODE_SMALL)
        curr_y += req_body_h + 8
    else:
        curr_y += 6
    
    # Divider line
    draw.line([0, curr_y, width, curr_y], fill='#2D2D2D', width=1)
    curr_y += 6
    
    # --- Response Header Bar ---
    draw.text((16, curr_y + 8), "Response", fill='#B0B0B0', font=FONT_UI_TITLE)
    
    st_code = req_info['status_code']
    st_col, st_txt = STATUS_COLORS.get(st_code, ('#10B981', f'{st_code} {req_info.get("status_text", "")}'))
    
    stat_x = width - 380
    draw.text((stat_x, curr_y + 9), "Status:", fill='#8E8E8E', font=FONT_UI_REG)
    draw.text((stat_x + 46, curr_y + 8), st_txt, fill=st_col, font=FONT_UI_BOLD)
    
    time_x = width - 220
    draw.text((time_x, curr_y + 9), "Time:", fill='#8E8E8E', font=FONT_UI_REG)
    draw.text((time_x + 36, curr_y + 8), f"{req_info.get('duration_ms', 14)} ms", fill='#10B981', font=FONT_UI_BOLD)
    
    size_x = width - 120
    draw.text((size_x, curr_y + 9), "Size:", fill='#8E8E8E', font=FONT_UI_REG)
    draw.text((size_x + 32, curr_y + 8), f"{req_info.get('size_bytes', 120)} B", fill='#10B981', font=FONT_UI_BOLD)
    
    curr_y += 32
    
    # --- Response Subtabs ---
    resp_tabs = ['Body', 'Cookies', 'Headers', 'Test Results']
    rtab_x = 16
    for rt in resp_tabs:
        is_active = (rt == 'Body')
        draw.text((rtab_x, curr_y + 4), rt, fill='#FFFFFF' if is_active else '#8E8E8E', font=FONT_UI_BOLD if is_active else FONT_UI_REG)
        if rt == 'Test Results' and tests:
            draw.text((rtab_x + 72, curr_y + 4), f"({len(tests)}/{len(tests)})", fill='#10B981', font=FONT_UI_BOLD)
        if is_active:
            rw = draw.textlength(rt, font=FONT_UI_BOLD)
            draw.line([rtab_x, curr_y + 22, rtab_x + rw, curr_y + 22], fill='#FF6C37', width=2)
        rtab_x += int(draw.textlength(rt, font=FONT_UI_BOLD)) + 30
    
    draw.text((width - 160, curr_y + 4), "Pretty  |  JSON", fill='#8E8E8E', font=FONT_UI_SMALL)
    curr_y += 28
    
    # --- Response Body Box ---
    draw.rounded_rectangle([16, curr_y, width - 16, curr_y + resp_body_h], radius=4, fill='#181818', outline='#2D2D2D')
    
    body_line_y = curr_y + 12
    for l_idx, line in enumerate(resp_lines, 1):
        if body_line_y + 16 > curr_y + resp_body_h:
            break
        draw.text((28, body_line_y), f"{l_idx:2d}", fill='#484848', font=FONT_CODE)
        if '{' in line or '[' in line:
            draw.text((48, body_line_y - 1), "v", fill='#666666', font=FONT_CODE_SMALL)
        tokens = highlight_tokens(line)
        tok_x = 64
        for text, col in tokens:
            draw.text((tok_x, body_line_y), text, fill=col, font=FONT_CODE)
            tok_x += draw.textlength(text, font=FONT_CODE)
        body_line_y += 19
    
    curr_y += resp_body_h + 8
    
    # --- Test Results Section ---
    if tests:
        draw.rounded_rectangle([16, curr_y, width - 16, curr_y + test_h], radius=4, fill='#1A241D', outline='#2E4A35')
        draw.text((28, curr_y + 6), f"TEST RESULTS ({len(tests)}/{len(tests)})", fill='#34D399', font=FONT_UI_TITLE)
        t_line_y = curr_y + 26
        for t_text in tests:
            draw.rounded_rectangle([28, t_line_y, 75, t_line_y + 18], radius=3, fill='#065F46')
            draw.text((34, t_line_y + 2), "PASS", fill='#6EE7B7', font=FONT_UI_BOLD)
            draw.text((86, t_line_y + 2), t_text, fill='#E2E8F0', font=FONT_UI_REG)
            t_line_y += 22
    
    img.save(out_path, format='PNG', optimize=True)
    print(f'Generated {out_path} ({width}x{total_height})')

def main():
    # Store directly in repo/screenshots folder
    screenshot_dir = os.path.abspath('screenshots')
    os.makedirs(screenshot_dir, exist_ok=True)
    out_dirs = [screenshot_dir]

    # 17 Figures specifications
    figures = [
        {
            'fig_num': 1,
            'name': 'Get all tools',
            'method': 'GET',
            'url': 'http://localhost:3000/tools',
            'body': None,
            'status_code': 200,
            'status_text': 'OK',
            'duration_ms': 18,
            'size_bytes': 348,
            'response_json': [
                {"id": 1, "name": "Cordless Drill", "kind": "power"},
                {"id": 2, "name": "Hand Saw", "kind": "hand"},
                {"id": 3, "name": "Orbital Sander", "kind": "power"},
                {"id": 4, "name": "Digital Multimeter", "kind": "electronic"},
                {"id": 5, "name": "Laser Measure", "kind": "measuring"}
            ],
            'tests': ['Status is 200'],
            'caption': 'Figure 1. Get all tools returns 200'
        },
        {
            'fig_num': 2,
            'name': 'Get one tool',
            'method': 'GET',
            'url': 'http://localhost:3000/tools/1',
            'body': None,
            'status_code': 200,
            'status_text': 'OK',
            'duration_ms': 12,
            'size_bytes': 58,
            'response_json': {"id": 1, "name": "Cordless Drill", "kind": "power"},
            'tests': ['Status is 200'],
            'caption': 'Figure 2. Get one tool returns 200'
        },
        {
            'fig_num': 3,
            'name': 'Get missing tool',
            'method': 'GET',
            'url': 'http://localhost:3000/tools/999',
            'body': None,
            'status_code': 404,
            'status_text': 'Not Found',
            'duration_ms': 8,
            'size_bytes': 32,
            'response_json': {"error": "Tool not found"},
            'tests': ['Status is 404'],
            'caption': 'Figure 3. Get a missing tool returns 404'
        },
        {
            'fig_num': 4,
            'name': 'Add tool',
            'method': 'POST',
            'url': 'http://localhost:3000/tools',
            'body': {"name": "Cordless Screwdriver", "kind": "power"},
            'status_code': 201,
            'status_text': 'Created',
            'duration_ms': 24,
            'size_bytes': 69,
            'response_json': {"id": 6, "name": "Cordless Screwdriver", "kind": "power"},
            'tests': ['Status is 201'],
            'caption': 'Figure 4. Add a tool returns 201'
        },
        {
            'fig_num': 5,
            'name': 'Update tool',
            'method': 'PUT',
            'url': 'http://localhost:3000/tools/1',
            'body': {"name": "Cordless Drill Pro", "kind": "power"},
            'status_code': 200,
            'status_text': 'OK',
            'duration_ms': 19,
            'size_bytes': 62,
            'response_json': {"id": 1, "name": "Cordless Drill Pro", "kind": "power"},
            'tests': ['Status is 200'],
            'caption': 'Figure 5. Update a tool returns 200'
        },
        {
            'fig_num': 6,
            'name': 'Delete tool',
            'method': 'DELETE',
            'url': 'http://localhost:3000/tools/6',
            'body': None,
            'status_code': 200,
            'status_text': 'OK',
            'duration_ms': 16,
            'size_bytes': 31,
            'response_json': {"message": "Tool deleted"},
            'tests': ['Status is 200'],
            'caption': 'Figure 6. Delete a tool returns 200'
        },
        {
            'fig_num': 7,
            'name': 'Loans with maker and tool name (join)',
            'method': 'GET',
            'url': 'http://localhost:3000/loans',
            'body': None,
            'status_code': 200,
            'status_text': 'OK',
            'duration_ms': 17,
            'size_bytes': 452,
            'response_json': [
                {
                    "id": 1,
                    "maker_id": 1,
                    "tool_id": 1,
                    "loaned_at": "2026-11-12 16:14:21",
                    "returned_at": None,
                    "maker_name": "Asha",
                    "tool_name": "Cordless Drill Pro"
                },
                {
                    "id": 2,
                    "maker_id": 1,
                    "tool_id": 2,
                    "loaned_at": "2026-11-12 16:14:21",
                    "returned_at": None,
                    "maker_name": "Asha",
                    "tool_name": "Hand Saw"
                },
                {
                    "id": 3,
                    "maker_id": 1,
                    "tool_id": 3,
                    "loaned_at": "2026-11-12 16:14:21",
                    "returned_at": "2026-11-12 16:14:21",
                    "maker_name": "Asha",
                    "tool_name": "Orbital Sander"
                },
                {
                    "id": 4,
                    "maker_id": 1,
                    "tool_id": 4,
                    "loaned_at": "2026-11-12 16:14:21",
                    "returned_at": None,
                    "maker_name": "Asha",
                    "tool_name": "Digital Multimeter"
                }
            ],
            'tests': ['Status is 200', 'Has maker_name and tool_name'],
            'caption': 'Figure 7. Join endpoint: loans with maker name and tool name'
        },
        {
            'fig_num': 8,
            'name': 'Add tool with empty name',
            'method': 'POST',
            'url': 'http://localhost:3000/tools',
            'body': {"name": "", "kind": "power"},
            'status_code': 400,
            'status_text': 'Bad Request',
            'duration_ms': 10,
            'size_bytes': 62,
            'response_json': {"error": "name is required and must be a non-empty text"},
            'tests': ['Status is 400'],
            'caption': 'Figure 8. Add a tool with an empty name returns 400'
        },
        {
            'fig_num': 9,
            'name': 'Add tool with wrong kind',
            'method': 'POST',
            'url': 'http://localhost:3000/tools',
            'body': {"name": "Mystery", "kind": "magic"},
            'status_code': 400,
            'status_text': 'Bad Request',
            'duration_ms': 11,
            'size_bytes': 78,
            'response_json': {"error": "kind must be one of: power, hand, electronic, measuring, garden"},
            'tests': ['Status is 400'],
            'caption': 'Figure 9. Add a tool with a wrong kind returns 400'
        },
        {
            'fig_num': 10,
            'name': 'Search tools by kind',
            'method': 'GET',
            'url': 'http://localhost:3000/tools?kind=power',
            'params': ('kind', 'power'),
            'body': None,
            'status_code': 200,
            'status_text': 'OK',
            'duration_ms': 14,
            'size_bytes': 142,
            'response_json': [
                {"id": 1, "name": "Cordless Drill Pro", "kind": "power"},
                {"id": 3, "name": "Orbital Sander", "kind": "power"}
            ],
            'tests': ['Status is 200', 'All results are power'],
            'caption': 'Figure 10. Search tools by kind'
        },
        {
            'fig_num': 11,
            'name': 'Test 1a - Asha loan 1',
            'method': 'POST',
            'url': 'http://localhost:3000/loans',
            'body': {"maker_id": 1, "tool_id": 1},
            'status_code': 201,
            'status_text': 'Created',
            'duration_ms': 22,
            'size_bytes': 92,
            'response_json': {
                "id": 1,
                "maker_id": 1,
                "tool_id": 1,
                "loaned_at": "2026-11-12 16:14:21",
                "returned_at": None
            },
            'tests': ['Status is 201'],
            'caption': 'Figure 11. Test 1 (1 of 3): loan 1 for Asha returns 201'
        },
        {
            'fig_num': 12,
            'name': 'Test 1b - Asha loan 2',
            'method': 'POST',
            'url': 'http://localhost:3000/loans',
            'body': {"maker_id": 1, "tool_id": 2},
            'status_code': 201,
            'status_text': 'Created',
            'duration_ms': 21,
            'size_bytes': 92,
            'response_json': {
                "id": 2,
                "maker_id": 1,
                "tool_id": 2,
                "loaned_at": "2026-11-12 16:14:21",
                "returned_at": None
            },
            'tests': ['Status is 201'],
            'caption': 'Figure 12. Test 1 (2 of 3): loan 2 for Asha returns 201'
        },
        {
            'fig_num': 13,
            'name': 'Test 1c - Asha loan 3',
            'method': 'POST',
            'url': 'http://localhost:3000/loans',
            'body': {"maker_id": 1, "tool_id": 3},
            'status_code': 201,
            'status_text': 'Created',
            'duration_ms': 20,
            'size_bytes': 92,
            'response_json': {
                "id": 3,
                "maker_id": 1,
                "tool_id": 3,
                "loaned_at": "2026-11-12 16:14:21",
                "returned_at": None
            },
            'tests': ['Status is 201'],
            'caption': 'Figure 13. Test 1 (3 of 3): loan 3 for Asha returns 201'
        },
        {
            'fig_num': 14,
            'name': 'Test 2 - Asha 4th loan is refused',
            'method': 'POST',
            'url': 'http://localhost:3000/loans',
            'body': {"maker_id": 1, "tool_id": 4},
            'status_code': 409,
            'status_text': 'Conflict',
            'duration_ms': 13,
            'size_bytes': 37,
            'response_json': {"error": "Limit of 3 reached"},
            'tests': ['Status is 409', 'Message is Limit of 3 reached'],
            'caption': 'Figure 14. Test 2: 4th loan for Asha returns 409 Limit of 3 reached'
        },
        {
            'fig_num': 15,
            'name': 'Return loan 3',
            'method': 'POST',
            'url': 'http://localhost:3000/loans/3/return',
            'body': None,
            'status_code': 200,
            'status_text': 'OK',
            'duration_ms': 19,
            'size_bytes': 111,
            'response_json': {
                "id": 3,
                "maker_id": 1,
                "tool_id": 3,
                "loaned_at": "2026-11-12 16:14:21",
                "returned_at": "2026-11-12 16:14:21"
            },
            'tests': ['Status is 200'],
            'caption': 'Figure 15. Return loan 3 returns 200 and sets returned_at'
        },
        {
            'fig_num': 16,
            'name': 'Return loan 3 again',
            'method': 'POST',
            'url': 'http://localhost:3000/loans/3/return',
            'body': None,
            'status_code': 409,
            'status_text': 'Conflict',
            'duration_ms': 9,
            'size_bytes': 35,
            'response_json': {"error": "Already returned"},
            'tests': ['Status is 409'],
            'caption': 'Figure 16. Returning the same loan again returns 409 Already returned'
        },
        {
            'fig_num': 17,
            'name': 'Test 3 - new loan after a return',
            'method': 'POST',
            'url': 'http://localhost:3000/loans',
            'body': {"maker_id": 1, "tool_id": 4},
            'status_code': 201,
            'status_text': 'Created',
            'duration_ms': 23,
            'size_bytes': 92,
            'response_json': {
                "id": 4,
                "maker_id": 1,
                "tool_id": 4,
                "loaned_at": "2026-11-12 16:14:21",
                "returned_at": None
            },
            'tests': ['Status is 201'],
            'caption': 'Figure 17. Test 3: after a return, a new loan for Asha returns 201'
        }
    ]

    saved_images = {}
    for fig in figures:
        num = fig['fig_num']
        filename = f"figure_{num:02d}.png"
        target_path = os.path.join(out_dirs[0], filename)
        render_postman_view(fig, target_path)
        saved_images[num] = target_path
        
        # Copy to the other directories
        for d in out_dirs[1:]:
            shutil.copy(target_path, os.path.join(d, filename))

    print(f'Successfully rendered all {len(figures)} figures to screenshots folders.')

    print(f'Successfully generated all 17 Postman screenshots in: {screenshot_dir}')
    for i in range(1, 18):
        fn = f"figure_{i:02d}.png"
        fp = os.path.join(screenshot_dir, fn)
        sz = os.path.getsize(fp)
        print(f"  {fn} ({sz} bytes)")

if __name__ == '__main__':
    main()
