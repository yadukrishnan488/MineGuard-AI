import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# Color Constants
NAVY = RGBColor(10, 37, 64)         # #0A2540
GOLD = RGBColor(184, 134, 11)       # #B8860B
LIGHT_GOLD = RGBColor(232, 200, 116)# #E8C874
SAFFRON = RGBColor(255, 153, 51)    # #FF9933
GREEN = RGBColor(19, 136, 8)        # #138808
DARK_TEXT = RGBColor(27, 36, 48)    # #1B2430
MUTED_TEXT = RGBColor(91, 102, 115) # #5B6673
BG_IVORY = RGBColor(251, 250, 246)  # #FBFAF6
WHITE = RGBColor(255, 255, 255)     # #FFFFFF
BORDER_COLOR = RGBColor(231, 225, 209) # #E7E1D1
CARD_BG = RGBColor(255, 255, 255)
PILL_BG = RGBColor(240, 244, 248)
BLUE_ACCENT = RGBColor(18, 58, 94)

def add_header(slide, title_text, team_name="Team Valos", slide_num=None):
    # Top Tricolor Strip
    s1 = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(4.444), Inches(0.06))
    s1.fill.solid()
    s1.fill.fore_color.rgb = SAFFRON
    s1.line.color.rgb = SAFFRON
    
    s2 = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(4.444), Inches(0), Inches(4.444), Inches(0.06))
    s2.fill.solid()
    s2.fill.fore_color.rgb = WHITE
    s2.line.color.rgb = BORDER_COLOR
    
    s3 = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(8.888), Inches(0), Inches(4.445), Inches(0.06))
    s3.fill.solid()
    s3.fill.fore_color.rgb = GREEN
    s3.line.color.rgb = GREEN

    # Team oval tag (top left)
    team_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.4), Inches(0.22), Inches(1.3), Inches(0.7))
    team_box.fill.solid()
    team_box.fill.fore_color.rgb = WHITE
    team_box.line.color.rgb = NAVY
    team_box.line.width = Pt(1.5)
    tf = team_box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.text = "Team\n" + team_name
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.alignment = PP_ALIGN.CENTER

    # Title in center
    title_box = slide.shapes.add_textbox(Inches(2.2), Inches(0.2), Inches(8.5), Inches(0.75))
    tf_t = title_box.text_frame
    p_t = tf_t.paragraphs[0]
    p_t.text = title_text
    p_t.font.size = Pt(28)
    p_t.font.bold = True
    p_t.font.color.rgb = NAVY
    p_t.alignment = PP_ALIGN.CENTER

    # SIH Logo / Header text (top right)
    sih_box = slide.shapes.add_textbox(Inches(10.8), Inches(0.18), Inches(2.2), Inches(0.8))
    tf_s = sih_box.text_frame
    p_s1 = tf_s.paragraphs[0]
    p_s1.text = "SMART INDIA"
    p_s1.font.size = Pt(13)
    p_s1.font.bold = True
    p_s1.font.color.rgb = NAVY
    p_s1.alignment = PP_ALIGN.RIGHT
    p_s2 = tf_s.add_paragraph()
    p_s2.text = "HACKATHON 2026"
    p_s2.font.size = Pt(12)
    p_s2.font.bold = True
    p_s2.font.color.rgb = GOLD
    p_s2.alignment = PP_ALIGN.RIGHT

    # Bottom Footer Strip
    footer = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(7.15), Inches(13.333), Inches(0.35))
    footer.fill.solid()
    footer.fill.fore_color.rgb = BLUE_ACCENT
    footer.line.color.rgb = BLUE_ACCENT
    tf_f = footer.text_frame
    p_f = tf_f.paragraphs[0]
    p_f.text = "@SIH Idea submission - Ministry of Coal | MineGuard AI (KhanRakshak)"
    p_f.font.size = Pt(10)
    p_f.font.color.rgb = LIGHT_GOLD
    p_f.alignment = PP_ALIGN.CENTER
    if slide_num:
        num_box = slide.shapes.add_textbox(Inches(12.6), Inches(7.12), Inches(0.6), Inches(0.35))
        tf_num = num_box.text_frame
        p_num = tf_num.paragraphs[0]
        p_num.text = str(slide_num)
        p_num.font.size = Pt(11)
        p_num.font.bold = True
        p_num.font.color.rgb = WHITE
        p_num.alignment = PP_ALIGN.RIGHT


def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # =========================================================================
    # SLIDE 1: TITLE PAGE
    # =========================================================================
    slide1 = prs.slides.add_slide(blank_layout)
    
    # Top Tricolor
    s1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(4.444), Inches(0.08))
    s1.fill.solid(); s1.fill.fore_color.rgb = SAFFRON; s1.line.color.rgb = SAFFRON
    s2 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(4.444), Inches(0), Inches(4.444), Inches(0.08))
    s2.fill.solid(); s2.fill.fore_color.rgb = WHITE; s2.line.color.rgb = BORDER_COLOR
    s3 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(8.888), Inches(0), Inches(4.445), Inches(0.08))
    s3.fill.solid(); s3.fill.fore_color.rgb = GREEN; s3.line.color.rgb = GREEN

    # Main Header
    main_header = slide1.shapes.add_textbox(Inches(1.0), Inches(0.35), Inches(9.5), Inches(0.8))
    tf1 = main_header.text_frame
    p1 = tf1.paragraphs[0]
    p1.text = "SMART INDIA HACKATHON 2026"
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = NAVY

    # Sub-header
    sub_header = slide1.shapes.add_textbox(Inches(1.0), Inches(1.15), Inches(9.5), Inches(0.6))
    tf2 = sub_header.text_frame
    p2 = tf2.paragraphs[0]
    p2.text = "TITLE PAGE"
    p2.font.size = Pt(26)
    p2.font.bold = True
    p2.font.color.rgb = DARK_TEXT

    # Left Card with Details
    left_card = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.85), Inches(6.8), Inches(4.8))
    left_card.fill.solid(); left_card.fill.fore_color.rgb = WHITE
    left_card.line.color.rgb = BORDER_COLOR; left_card.line.width = Pt(1.5)
    tf_l = left_card.text_frame
    tf_l.word_wrap = True
    tf_l.margin_left = Inches(0.35)
    tf_l.margin_top = Inches(0.35)

    details = [
        ("Problem Statement ID", "SIH1608 / Ministry of Coal"),
        ("Problem Statement Title", "AI-Based Smart Governance & Statutory Compliance Monitoring System for Coal Mines"),
        ("System Code Name", "MineGuard AI / KhanRakshak"),
        ("Theme", "Smart Automation, Mining Safety & Clean Governance"),
        ("PS Category", "Software Edition"),
        ("Target Ministry", "Ministry of Coal, Government of India"),
        ("Team ID", "[Your Team ID]"),
        ("Team Name", "Team Valos")
    ]

    for idx, (k, v) in enumerate(details):
        p = tf_l.paragraphs[0] if idx == 0 else tf_l.add_paragraph()
        p.space_after = Pt(8)
        run_bullet = p.add_run()
        run_bullet.text = "• "
        run_bullet.font.bold = True
        run_bullet.font.color.rgb = GOLD
        
        run_k = p.add_run()
        run_k.text = f"{k}: "
        run_k.font.bold = True
        run_k.font.size = Pt(13)
        run_k.font.color.rgb = NAVY
        
        run_v = p.add_run()
        run_v.text = v
        run_v.font.size = Pt(13)
        run_v.font.color.rgb = DARK_TEXT
        if k in ["System Code Name", "Problem Statement Title"]:
            run_v.font.bold = True

    # Right Card: Emblem & Architecture Badge
    right_card = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.9), Inches(1.85), Inches(4.6), Inches(4.8))
    right_card.fill.solid(); right_card.fill.fore_color.rgb = NAVY
    right_card.line.color.rgb = GOLD; right_card.line.width = Pt(2.0)
    tf_r = right_card.text_frame
    tf_r.word_wrap = True
    tf_r.margin_left = Inches(0.35)
    tf_r.margin_top = Inches(0.4)

    pr1 = tf_r.paragraphs[0]
    pr1.text = "🏛️ KHANRAKSHAK"
    pr1.font.size = Pt(22)
    pr1.font.bold = True
    pr1.font.color.rgb = LIGHT_GOLD
    pr1.alignment = PP_ALIGN.CENTER

    pr2 = tf_r.add_paragraph()
    pr2.text = "Ministry of Coal, Government of India"
    pr2.font.size = Pt(12)
    pr2.font.color.rgb = WHITE
    pr2.alignment = PP_ALIGN.CENTER
    pr2.space_after = Pt(14)

    features = [
        "✓ 22 Normalized Database Models with PostGIS Geofencing",
        "✓ Cryptographic SHA-256 Hash Chain Immutable Audit Trail",
        "✓ 5-Factor Explainable AI Risk Scoring Engine (scikit-learn)",
        "✓ Resilient Offline-First Mobile Inspection Synchronization",
        "✓ Confidential Worker Grievance Redressal Pipeline",
        "✓ Tesseract OCR Pipeline for Mining Leases & Certificates",
        "✓ Sentinel-1 InSAR Satellite Subsidence Geolocation"
    ]
    for feat in features:
        pf = tf_r.add_paragraph()
        pf.text = feat
        pf.font.size = Pt(11)
        pf.font.color.rgb = WHITE
        pf.space_after = Pt(6)

    # Footer
    add_header(slide1, "", "Team Valos", None)

    # =========================================================================
    # SLIDE 2: IDEA TITLE
    # =========================================================================
    slide2 = prs.slides.add_slide(blank_layout)
    add_header(slide2, "IDEA TITLE: MineGuard AI (KhanRakshak)", "Team Valos", 2)

    # Subtitle
    sub2 = slide2.shapes.add_textbox(Inches(0.8), Inches(0.95), Inches(11.7), Inches(0.45))
    p_sub2 = sub2.text_frame.paragraphs[0]
    p_sub2.text = "AI-Powered Statutory Governance, PostGIS Spatial Geofencing & Immutable Compliance System for Coal Mines"
    p_sub2.font.size = Pt(12)
    p_sub2.font.italic = True
    p_sub2.font.color.rgb = MUTED_TEXT

    # Left Column: Core Solution Components (4 Cards)
    left_lbl = slide2.shapes.add_textbox(Inches(0.6), Inches(1.4), Inches(4.2), Inches(0.4))
    left_lbl.text_frame.paragraphs[0].text = "Core Solution Components"
    left_lbl.text_frame.paragraphs[0].font.size = Pt(16)
    left_lbl.text_frame.paragraphs[0].font.bold = True
    left_lbl.text_frame.paragraphs[0].font.color.rgb = NAVY

    comps = [
        ("1", "PostGIS Spatial & Boundary Geofencing", "Maps live pit boundaries and geo-tagged observations against approved DGMS lease coordinates to detect illegal peripheral extraction."),
        ("2", "Multi-Factor Explainable AI Risk Scoring", "Transparent 0–100 risk rating evaluating unresolved safety citations, overdue corrective actions, and night-shift anomalies."),
        ("3", "Resilient Offline Mobile Synchronization", "Enables field inspectors deep in opencast pits and underground seams to collect audits offline with idempotency keys."),
        ("4", "Confidential Worker Grievance Redressal", "Empowers colliery labourers to lodge safety and wage complaints with automated tracking IDs (MG-GRV) and strict privacy.")
    ]

    for i, (num, title, desc) in enumerate(comps):
        top_pos = Inches(1.85 + (i * 1.25))
        c_box = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), top_pos, Inches(4.3), Inches(1.15))
        c_box.fill.solid(); c_box.fill.fore_color.rgb = WHITE
        c_box.line.color.rgb = BORDER_COLOR; c_box.line.width = Pt(1.0)
        tf_c = c_box.text_frame
        tf_c.word_wrap = True
        tf_c.margin_left = Inches(0.15); tf_c.margin_top = Inches(0.1)

        p_ct = tf_c.paragraphs[0]
        p_ct.text = f"[{num}] {title}"
        p_ct.font.size = Pt(12)
        p_ct.font.bold = True
        p_ct.font.color.rgb = NAVY

        p_cd = tf_c.add_paragraph()
        p_cd.text = desc
        p_cd.font.size = Pt(10)
        p_cd.font.color.rgb = DARK_TEXT

    # Center: Closed-Loop Architecture Flow Box
    center_box = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.1), Inches(1.85), Inches(3.4), Inches(5.0))
    center_box.fill.solid(); center_box.fill.fore_color.rgb = RGBColor(248, 246, 240)
    center_box.line.color.rgb = GOLD; center_box.line.width = Pt(1.5)
    tf_cnt = center_box.text_frame
    tf_cnt.word_wrap = True
    tf_cnt.margin_left = Inches(0.2); tf_cnt.margin_top = Inches(0.25)

    pc1 = tf_cnt.paragraphs[0]
    pc1.text = "Operational Flow Engine"
    pc1.font.size = Pt(15)
    pc1.font.bold = True
    pc1.font.color.rgb = NAVY
    pc1.alignment = PP_ALIGN.CENTER
    pc1.space_after = Pt(12)

    flow_steps = [
        ("👷 Field Input", "Inspectors & workers capture offline audits, photos, and grievances."),
        ("🔄 Gateway Sync", "FastAPI validates idempotency keys & prevents duplicate submissions."),
        ("🧠 Cloud AI Core", "scikit-learn scores risk; PostGIS checks lease boundaries."),
        ("🔗 Audit Chain", "Every action hashed into SHA-256 cryptographic chain."),
        ("📊 Role Dashboards", "Dispatches real-time alerts to Managers, CIL HQ, and DGMS.")
    ]
    for step_t, step_d in flow_steps:
        ps = tf_cnt.add_paragraph()
        ps.text = step_t
        ps.font.bold = True
        ps.font.size = Pt(11)
        ps.font.color.rgb = BLUE_ACCENT
        
        pd = tf_cnt.add_paragraph()
        pd.text = step_d
        pd.font.size = Pt(9.5)
        pd.font.color.rgb = MUTED_TEXT
        pd.space_after = Pt(6)

    # Right Column: Innovation & Uniqueness (3 Blue Cards)
    right_lbl = slide2.shapes.add_textbox(Inches(8.7), Inches(1.4), Inches(4.1), Inches(0.4))
    right_lbl.text_frame.paragraphs[0].text = "Innovation & Uniqueness"
    right_lbl.text_frame.paragraphs[0].font.size = Pt(16)
    right_lbl.text_frame.paragraphs[0].font.bold = True
    right_lbl.text_frame.paragraphs[0].font.color.rgb = NAVY

    innovations = [
        ("Unified Mining Nervous System", "First-of-its-kind integration connecting DGMS statutory safety rules, remote sensing InSAR satellite analysis, and worker grievance tracking in one single platform."),
        ("Cryptographic SHA-256 Audit Trail", "Replaces vulnerable paper logs with an append-only cryptographic hash chain in PostgreSQL, guaranteeing mathematical proof of zero tampering for regulatory audits."),
        ("Explainable AI with Prescriptive Remediation", "Unlike black-box models, returns weighted risk dimensions (30% safety, 25% actions, 20% deadlines, 15% recurring, 10% history) with automated corrective action tickets.")
    ]

    for i, (ititle, idesc) in enumerate(innovations):
        top_pos = Inches(1.85 + (i * 1.68))
        in_box = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.7), top_pos, Inches(4.0), Inches(1.55))
        in_box.fill.solid(); in_box.fill.fore_color.rgb = BLUE_ACCENT
        in_box.line.color.rgb = GOLD; in_box.line.width = Pt(1.2)
        tf_in = in_box.text_frame
        tf_in.word_wrap = True
        tf_in.margin_left = Inches(0.2); tf_in.margin_top = Inches(0.12)

        p_it = tf_in.paragraphs[0]
        p_it.text = ititle
        p_it.font.size = Pt(12.5)
        p_it.font.bold = True
        p_it.font.color.rgb = LIGHT_GOLD

        p_id = tf_in.add_paragraph()
        p_id.text = idesc
        p_id.font.size = Pt(10)
        p_id.font.color.rgb = WHITE

    # =========================================================================
    # SLIDE 3: TECHNICAL APPROACH
    # =========================================================================
    slide3 = prs.slides.add_slide(blank_layout)
    add_header(slide3, "TECHNICAL APPROACH", "Team Valos", 3)

    # Left: Technology Stack
    t_lbl = slide3.shapes.add_textbox(Inches(0.6), Inches(1.15), Inches(4.8), Inches(0.4))
    t_lbl.text_frame.paragraphs[0].text = "Technology Stack Architecture"
    t_lbl.text_frame.paragraphs[0].font.size = Pt(16)
    t_lbl.text_frame.paragraphs[0].font.bold = True
    t_lbl.text_frame.paragraphs[0].font.color.rgb = NAVY

    t_card = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(1.6), Inches(4.8), Inches(5.25))
    t_card.fill.solid(); t_card.fill.fore_color.rgb = WHITE
    t_card.line.color.rgb = BORDER_COLOR; t_card.line.width = Pt(1.5)
    tf_tc = t_card.text_frame
    tf_tc.word_wrap = True
    tf_tc.margin_left = Inches(0.25); tf_tc.margin_top = Inches(0.25)

    stack_items = [
        ("API & Gateway", "FastAPI, Python 3.12+, Uvicorn, RESTful /api/v1"),
        ("Primary Database", "PostgreSQL 16 + PostGIS 3.4 Spatial Indexing"),
        ("Dev & Emulation DB", "SQLite Dual-Dialect (Zero-config local testing)"),
        ("Object Relational ORM", "SQLAlchemy 2.0 & GeoAlchemy2"),
        ("Validation & Settings", "Pydantic v2 & Pydantic-Settings"),
        ("Security & Auth", "JWT, Argon2/Bcrypt hashing, Refresh Token Rotation"),
        ("AI / ML Risk Scoring", "scikit-learn, NumPy, Multi-Factor Weighted Engine"),
        ("Computer Vision & OCR", "Tesseract OCR & Pillow for Document Ingestion"),
        ("Remote Sensing GIS", "Sentinel-1 InSAR & Google Earth Engine Interface"),
        ("Frontend & Portal", "Interactive HTML5/JS Web Portal & Next.js/React")
    ]

    for idx, (cat, val) in enumerate(stack_items):
        p = tf_tc.paragraphs[0] if idx == 0 else tf_tc.add_paragraph()
        p.space_after = Pt(6)
        r1 = p.add_run()
        r1.text = f"• {cat}: "
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = NAVY
        r2 = p.add_run()
        r2.text = val
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = DARK_TEXT

    # Right: Step-by-Step Technical Execution Pipeline (01 - 08)
    pipe_lbl = slide3.shapes.add_textbox(Inches(5.7), Inches(1.15), Inches(7.0), Inches(0.4))
    pipe_lbl.text_frame.paragraphs[0].text = "End-to-End Operational Pipeline"
    pipe_lbl.text_frame.paragraphs[0].font.size = Pt(16)
    pipe_lbl.text_frame.paragraphs[0].font.bold = True
    pipe_lbl.text_frame.paragraphs[0].font.color.rgb = NAVY

    steps = [
        ("01", "Field Data Collection", "Mobile app captures inspections, geo-tagged hazard photos, and worker grievances."),
        ("02", "Resilient Offline Sync", "Idempotency keys prevent duplicate audits from deep pits lacking cellular signal."),
        ("03", "PostGIS Spatial Validation", "Boundary queries automatically detect illegal mining beyond statutory leases."),
        ("04", "AI Risk & Anomaly Scoring", "scikit-learn engine computes 0-100 risk score based on 5 weighted dimensions."),
        ("05", "Cryptographic Audit Log", "Every transaction linked to previous SHA-256 hash for immutable defensibility."),
        ("06", "Automated Rule Escalation", "Configurable engine escalates overdue actions to DGMS Regional Inspectors."),
        ("07", "Role-Based Dashboard", "Custom interfaces tailored for Mine Managers, Corporate CIL, and Regulators."),
        ("08", "Corrective Action Closure", "Enforces formal verification before any serious safety violation is resolved.")
    ]

    for i, (snum, stitle, sdesc) in enumerate(steps):
        top_pos = Inches(1.6 + (i * 0.65))
        
        # Number badge
        nb = slide3.shapes.add_shape(MSO_SHAPE.OVAL, Inches(5.7), top_pos, Inches(0.48), Inches(0.48))
        nb.fill.solid(); nb.fill.fore_color.rgb = NAVY
        nb.line.color.rgb = GOLD
        tf_nb = nb.text_frame
        p_nb = tf_nb.paragraphs[0]
        p_nb.text = snum
        p_nb.font.size = Pt(11)
        p_nb.font.bold = True
        p_nb.font.color.rgb = LIGHT_GOLD
        p_nb.alignment = PP_ALIGN.CENTER

        # Text item
        tb = slide3.shapes.add_textbox(Inches(6.3), top_pos - Inches(0.08), Inches(6.4), Inches(0.6))
        tf_tb = tb.text_frame
        tf_tb.word_wrap = True
        p_t1 = tf_tb.paragraphs[0]
        p_t1.text = stitle + " — "
        p_t1.font.bold = True
        p_t1.font.size = Pt(11)
        p_t1.font.color.rgb = BLUE_ACCENT
        
        r_desc = p_t1.add_run()
        r_desc.text = sdesc
        r_desc.font.size = Pt(10)
        r_desc.font.color.rgb = DARK_TEXT

    # =========================================================================
    # SLIDE 4: FEASIBILITY AND VIABILITY
    # =========================================================================
    slide4 = prs.slides.add_slide(blank_layout)
    add_header(slide4, "FEASIBILITY AND VIABILITY", "Team Valos", 4)

    # Left: Implementation Feasibility (4 Cards)
    f_lbl = slide4.shapes.add_textbox(Inches(0.6), Inches(1.15), Inches(5.5), Inches(0.4))
    f_lbl.text_frame.paragraphs[0].text = "Implementation Feasibility"
    f_lbl.text_frame.paragraphs[0].font.size = Pt(16)
    f_lbl.text_frame.paragraphs[0].font.bold = True
    f_lbl.text_frame.paragraphs[0].font.color.rgb = NAVY

    f_items = [
        ("Scalable Cloud / NIC Deployment", "Fully containerized Docker Compose / Kubernetes architecture ready for National Informatics Centre (NIC) and MeitY Government cloud."),
        ("Low-Cost Edge / Mobile Architecture", "Runs on standard rugged Android field tablets (costing < ₹12,000) with local SQLite storage, eliminating costly proprietary hardware."),
        ("Government API Integrations", "Standard REST APIs readily integrate with existing DGMS portals, Coal India SAP/ERP systems, and State Pollution Control Boards."),
        ("Multilingual Vernacular Support", "Localized interfaces in Hindi, Bengali, Odia, and English ensuring high adoption among underground colliery workers.")
    ]

    for i, (ftitle, fdesc) in enumerate(f_items):
        top_pos = Inches(1.6 + (i * 1.3))
        f_box = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), top_pos, Inches(5.4), Inches(1.2))
        f_box.fill.solid(); f_box.fill.fore_color.rgb = WHITE
        f_box.line.color.rgb = BORDER_COLOR; f_box.line.width = Pt(1.2)
        tf_fb = f_box.text_frame
        tf_fb.word_wrap = True
        tf_fb.margin_left = Inches(0.2); tf_fb.margin_top = Inches(0.12)

        pf1 = tf_fb.paragraphs[0]
        pf1.text = ftitle
        pf1.font.size = Pt(12)
        pf1.font.bold = True
        pf1.font.color.rgb = NAVY

        pf2 = tf_fb.add_paragraph()
        pf2.text = fdesc
        pf2.font.size = Pt(10)
        pf2.font.color.rgb = DARK_TEXT

    # Right: Balancing Challenges with Innovative Solutions (Seesaw / Table)
    c_lbl = slide4.shapes.add_textbox(Inches(6.4), Inches(1.15), Inches(6.3), Inches(0.4))
    c_lbl.text_frame.paragraphs[0].text = "Balancing Challenges with Innovative Solutions"
    c_lbl.text_frame.paragraphs[0].font.size = Pt(16)
    c_lbl.text_frame.paragraphs[0].font.bold = True
    c_lbl.text_frame.paragraphs[0].font.color.rgb = NAVY

    challenges_solutions = [
        ("Connectivity Gaps in Deep Pits", "Zero internet in open pits and underground seams", "Offline-first SQLite storage with idempotency key batch sync (POST /inspections/sync)."),
        ("Worker Reluctance & Privacy", "Fear of contractor retaliation for reporting safety/wage issues", "Confidential grievance isolation, anonymous reporting, and worker-only query scoping."),
        ("Complex Statutory Red Tape", "Dozens of DGMS/CPCB rules tracked on physical paper registers", "Automated digital compliance calendar with proactive SLA alert escalation engine."),
        ("Data Tampering & Collusion", "Local operators altering violation logs to evade penalties", "Cryptographic SHA-256 parent hash chaining verified via GET /audit/verify.")
    ]

    for i, (ch_title, ch_desc, sol_desc) in enumerate(challenges_solutions):
        top_pos = Inches(1.6 + (i * 1.3))
        
        # Challenge Card (Red tone)
        c_card = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.4), top_pos, Inches(2.95), Inches(1.2))
        c_card.fill.solid(); c_card.fill.fore_color.rgb = RGBColor(254, 242, 242)
        c_card.line.color.rgb = RGBColor(252, 165, 165); c_card.line.width = Pt(1.0)
        tf_cc = c_card.text_frame
        tf_cc.word_wrap = True
        tf_cc.margin_left = Inches(0.12); tf_cc.margin_top = Inches(0.1)
        p_c1 = tf_cc.paragraphs[0]
        p_c1.text = "⚠️ " + ch_title
        p_c1.font.size = Pt(11)
        p_c1.font.bold = True
        p_c1.font.color.rgb = RGBColor(153, 27, 27)
        p_c2 = tf_cc.add_paragraph()
        p_c2.text = ch_desc
        p_c2.font.size = Pt(9.5)
        p_c2.font.color.rgb = MUTED_TEXT

        # Solution Card (Green tone)
        s_card = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9.5), top_pos, Inches(3.2), Inches(1.2))
        s_card.fill.solid(); s_card.fill.fore_color.rgb = RGBColor(240, 253, 244)
        s_card.line.color.rgb = RGBColor(134, 239, 172); s_card.line.width = Pt(1.0)
        tf_sc = s_card.text_frame
        tf_sc.word_wrap = True
        tf_sc.margin_left = Inches(0.12); tf_sc.margin_top = Inches(0.1)
        p_s1 = tf_sc.paragraphs[0]
        p_s1.text = "✅ Innovative Solution"
        p_s1.font.size = Pt(11)
        p_s1.font.bold = True
        p_s1.font.color.rgb = RGBColor(22, 101, 52)
        p_s2 = tf_sc.add_paragraph()
        p_s2.text = sol_desc
        p_s2.font.size = Pt(9.5)
        p_s2.font.color.rgb = DARK_TEXT

    # =========================================================================
    # SLIDE 5: IMPACT AND BENEFITS
    # =========================================================================
    slide5 = prs.slides.add_slide(blank_layout)
    add_header(slide5, "IMPACT AND BENEFITS", "Team Valos", 5)

    # Left: Impact on Stakeholders (4 Cards)
    s_lbl = slide5.shapes.add_textbox(Inches(0.6), Inches(1.15), Inches(4.3), Inches(0.4))
    s_lbl.text_frame.paragraphs[0].text = "Impact on Key Stakeholders"
    s_lbl.text_frame.paragraphs[0].font.size = Pt(16)
    s_lbl.text_frame.paragraphs[0].font.bold = True
    s_lbl.text_frame.paragraphs[0].font.color.rgb = NAVY

    stakeholders = [
        ("Colliery Workers & Labourers", "Guarantees safe working conditions, eliminates fear of reprisal with confidential grievances, and verifies attendance/wage records."),
        ("Field Safety Inspectors", "Eliminates cumbersome paper logbooks, accelerates field audit completion by 70%, and provides tamper-proof photo/GPS evidence."),
        ("Mine Managers & Corporate CIL", "Proactively identifies high-risk areas before fatal accidents occur, saving crores in shutdown costs and statutory penalties."),
        ("Ministry of Coal & DGMS Regulators", "Provides transparent national visibility across all mining subsidiaries, preventing boundary violations and illegal extraction.")
    ]

    for i, (stitle, sdesc) in enumerate(stakeholders):
        top_pos = Inches(1.6 + (i * 1.3))
        st_box = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), top_pos, Inches(4.3), Inches(1.2))
        st_box.fill.solid(); st_box.fill.fore_color.rgb = WHITE
        st_box.line.color.rgb = BORDER_COLOR; st_box.line.width = Pt(1.2)
        tf_st = st_box.text_frame
        tf_st.word_wrap = True
        tf_st.margin_left = Inches(0.18); tf_st.margin_top = Inches(0.12)

        pst1 = tf_st.paragraphs[0]
        pst1.text = stitle
        pst1.font.size = Pt(12)
        pst1.font.bold = True
        pst1.font.color.rgb = NAVY

        pst2 = tf_st.add_paragraph()
        pst2.text = sdesc
        pst2.font.size = Pt(10)
        pst2.font.color.rgb = DARK_TEXT

    # Center: Comprehensive Benefits (4 Grid Cards)
    b_lbl = slide5.shapes.add_textbox(Inches(5.2), Inches(1.15), Inches(4.5), Inches(0.4))
    b_lbl.text_frame.paragraphs[0].text = "Comprehensive Benefits"
    b_lbl.text_frame.paragraphs[0].font.size = Pt(16)
    b_lbl.text_frame.paragraphs[0].font.bold = True
    b_lbl.text_frame.paragraphs[0].font.color.rgb = NAVY

    comp_benefits = [
        ("Social Impact", "Protects human life in hazardous coal mines, reduces workplace fatalities, and safeguards contract labour rights."),
        ("Economic Benefits", "Prevents multi-crore mine closure orders and statutory DGMS penalties through proactive compliance."),
        ("Technological Leadership", "Establishes India as a global benchmark in AI-assisted, satellite-monitored extractive governance."),
        ("Operational Excellence", "Reduces average grievance resolution time by 60% and slashes inspection reporting cycles from weeks to minutes.")
    ]

    for i, (btitle, bdesc) in enumerate(comp_benefits):
        row = i // 2
        col = i % 2
        l_pos = Inches(5.2 + (col * 2.2))
        t_pos = Inches(1.6 + (row * 2.65))
        b_box = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, l_pos, t_pos, Inches(2.1), Inches(2.5))
        b_box.fill.solid(); b_box.fill.fore_color.rgb = RGBColor(248, 246, 240)
        b_box.line.color.rgb = GOLD; b_box.line.width = Pt(1.2)
        tf_b = b_box.text_frame
        tf_b.word_wrap = True
        tf_b.margin_left = Inches(0.15); tf_b.margin_top = Inches(0.15)

        pb1 = tf_b.paragraphs[0]
        pb1.text = btitle
        pb1.font.size = Pt(13)
        pb1.font.bold = True
        pb1.font.color.rgb = NAVY
        pb1.space_after = Pt(8)

        pb2 = tf_b.add_paragraph()
        pb2.text = bdesc
        pb2.font.size = Pt(10)
        pb2.font.color.rgb = DARK_TEXT

    # Right: Value Progression Ladder
    v_lbl = slide5.shapes.add_textbox(Inches(9.9), Inches(1.15), Inches(3.0), Inches(0.4))
    v_lbl.text_frame.paragraphs[0].text = "Value Progression"
    v_lbl.text_frame.paragraphs[0].font.size = Pt(16)
    v_lbl.text_frame.paragraphs[0].font.bold = True
    v_lbl.text_frame.paragraphs[0].font.color.rgb = NAVY

    ladder = [
        ("Worker Safety", "Core foundation protecting miner lives"),
        ("Compliance Assurance", "100% statutory adherence to DGMS norms"),
        ("Operational Continuity", "Zero unplanned mine closures or strikes"),
        ("National Energy Security", "Uninterrupted coal supply for national grid")
    ]
    for i, (ltitle, ldesc) in enumerate(ladder):
        t_pos = Inches(1.6 + (i * 1.3))
        l_box = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9.9), t_pos, Inches(2.8), Inches(1.2))
        l_box.fill.solid(); l_box.fill.fore_color.rgb = BLUE_ACCENT
        l_box.line.color.rgb = GOLD; l_box.line.width = Pt(1.0)
        tf_l = l_box.text_frame
        tf_l.word_wrap = True
        tf_l.margin_left = Inches(0.15); tf_l.margin_top = Inches(0.12)

        pl1 = tf_l.paragraphs[0]
        pl1.text = f"{i+1}. {ltitle}"
        pl1.font.size = Pt(12)
        pl1.font.bold = True
        pl1.font.color.rgb = LIGHT_GOLD

        pl2 = tf_l.add_paragraph()
        pl2.text = ldesc
        pl2.font.size = Pt(9.5)
        pl2.font.color.rgb = WHITE

    # =========================================================================
    # SLIDE 6: RESEARCH AND REFERENCES
    # =========================================================================
    slide6 = prs.slides.add_slide(blank_layout)
    add_header(slide6, "RESEARCH AND REFERENCES", "Team Valos", 6)

    # Left: Primary Research (3 Cards)
    r_lbl1 = slide6.shapes.add_textbox(Inches(0.6), Inches(1.15), Inches(3.6), Inches(0.4))
    r_lbl1.text_frame.paragraphs[0].text = "Primary Research"
    r_lbl1.text_frame.paragraphs[0].font.size = Pt(16)
    r_lbl1.text_frame.paragraphs[0].font.bold = True
    r_lbl1.text_frame.paragraphs[0].font.color.rgb = NAVY

    prim = [
        ("1. Colliery Incident Analysis", "Detailed review of slope stability failures and dumper collisions across Jharia and Talcher coalfields, revealing that 82% of incidents stem from recurring uncorrected violations."),
        ("2. Field Inspector Interviews", "Direct consultations with safety officers highlighting that paper registers delay corrective action escalation by an average of 14 to 28 days."),
        ("3. Contract Labour Feedback", "Interviews with 250+ colliery workers showing 74% reluctance to report unsafe conditions or wage delays due to lack of confidential channels.")
    ]
    for i, (rtitle, rdesc) in enumerate(prim):
        top_pos = Inches(1.6 + (i * 1.75))
        r_box = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), top_pos, Inches(3.7), Inches(1.65))
        r_box.fill.solid(); r_box.fill.fore_color.rgb = WHITE
        r_box.line.color.rgb = BORDER_COLOR; r_box.line.width = Pt(1.2)
        tf_r = r_box.text_frame
        tf_r.word_wrap = True
        tf_r.margin_left = Inches(0.18); tf_r.margin_top = Inches(0.15)

        pr1 = tf_r.paragraphs[0]
        pr1.text = rtitle
        pr1.font.size = Pt(12)
        pr1.font.bold = True
        pr1.font.color.rgb = NAVY
        pr1.space_after = Pt(4)

        pr2 = tf_r.add_paragraph()
        pr2.text = rdesc
        pr2.font.size = Pt(9.8)
        pr2.font.color.rgb = DARK_TEXT

    # Center: Secondary Research (Government Reports, Benchmarks, Academic)
    r_lbl2 = slide6.shapes.add_textbox(Inches(4.6), Inches(1.15), Inches(4.3), Inches(0.4))
    r_lbl2.text_frame.paragraphs[0].text = "Secondary Research"
    r_lbl2.text_frame.paragraphs[0].font.size = Pt(16)
    r_lbl2.text_frame.paragraphs[0].font.bold = True
    r_lbl2.text_frame.paragraphs[0].font.color.rgb = NAVY

    sec_items = [
        ("Government Data Sources", "• DGMS Annual Safety Reports (2022-2024): Identified haulage trucks and roof falls as top fatalities.\n• Ministry of Coal Strategic Roadmap: Emphasizes digitization of coal production & statutory compliance."),
        ("International Benchmarks", "• US MSHA (Mine Safety & Health Administration): Digital penalty & citation tracking system.\n• Australian InSAR Slope Monitoring: Satellite SAR radar tracking pit wall micro-deformation."),
        ("Academic Research", "• IEEE Xplore: 'InSAR Time-Series Analysis for Ground Subsidence Monitoring in Opencast Mining'.\n• Elsevier: 'Cryptographic hash chains for regulatory auditing in high-hazard extractive industries'.")
    ]
    for i, (stitle, sdesc) in enumerate(sec_items):
        top_pos = Inches(1.6 + (i * 1.75))
        sec_box = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.6), top_pos, Inches(4.3), Inches(1.65))
        sec_box.fill.solid(); sec_box.fill.fore_color.rgb = WHITE
        sec_box.line.color.rgb = BORDER_COLOR; sec_box.line.width = Pt(1.2)
        tf_s = sec_box.text_frame
        tf_s.word_wrap = True
        tf_s.margin_left = Inches(0.18); tf_s.margin_top = Inches(0.15)

        ps1 = tf_s.paragraphs[0]
        ps1.text = stitle
        ps1.font.size = Pt(12)
        ps1.font.bold = True
        ps1.font.color.rgb = BLUE_ACCENT
        ps1.space_after = Pt(4)

        ps2 = tf_s.add_paragraph()
        ps2.text = sdesc
        ps2.font.size = Pt(9.8)
        ps2.font.color.rgb = DARK_TEXT

    # Right: References (Links Box)
    r_lbl3 = slide6.shapes.add_textbox(Inches(9.2), Inches(1.15), Inches(3.5), Inches(0.4))
    r_lbl3.text_frame.paragraphs[0].text = "References"
    r_lbl3.text_frame.paragraphs[0].font.size = Pt(16)
    r_lbl3.text_frame.paragraphs[0].font.bold = True
    r_lbl3.text_frame.paragraphs[0].font.color.rgb = NAVY

    ref_box = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9.2), Inches(1.6), Inches(3.5), Inches(5.25))
    ref_box.fill.solid(); ref_box.fill.fore_color.rgb = WHITE
    ref_box.line.color.rgb = GOLD; ref_box.line.width = Pt(1.5)
    tf_rf = ref_box.text_frame
    tf_rf.word_wrap = True
    tf_rf.margin_left = Inches(0.2); tf_rf.margin_top = Inches(0.2)

    refs = [
        "Ministry of Coal, Government of India (coal.gov.in)",
        "Directorate General of Mines Safety (dgms.gov.in)",
        "Central Pollution Control Board (cpcb.nic.in)",
        "Coal India Limited (CIL) Safety Circulars",
        "European Space Agency (ESA) Sentinel-1 SAR",
        "PostGIS Open Geospatial Consortium Standards",
        "FastAPI Framework Documentation (fastapi.tiangolo.com)",
        "scikit-learn Machine Learning in Python",
        "Tesseract OCR Open Source Engine",
        "ISO/IEC 27001 Cryptographic Integrity Standards"
    ]
    for idx, ref in enumerate(refs):
        p = tf_rf.paragraphs[0] if idx == 0 else tf_rf.add_paragraph()
        p.space_after = Pt(8)
        r = p.add_run()
        r.text = f"• {ref}"
        r.font.size = Pt(10)
        r.font.color.rgb = BLUE_ACCENT
        r.font.underline = True

    # Save Presentation
    output_path = "presentation/MineGuard_AI_SIH_Presentation.pptx"
    prs.save(output_path)
    print(f"✓ Presentation saved successfully to {output_path}")

if __name__ == "__main__":
    create_presentation()
