from aqt import mw

def apply_apple_style(widget):
    """应用苹果风格样式"""
    # 检测Anki是否处于夜间模式
    night_mode = False
    try:
        from aqt.theme import theme_manager
        night_mode = theme_manager.night_mode
    except:
        try:
            night_mode = mw.pm.meta.get("night_mode", False)
        except:
            pass

    try:
        if night_mode:
            # 深色模式样式
            widget.setStyleSheet("""
            QDialog { 
                background-color: #1E1E1E; 
                color: #FFFFFF; 
            }
            QLabel { 
                color: #FFFFFF; 
                font-size: 13px;
            }
            QGroupBox { 
                background-color: #2C2C2E; 
                border-radius: 10px; 
                color: #FFFFFF; 
                font-size: 14px;
                padding-top: 15px; 
                margin-top: 15px; 
            }
            QGroupBox::title { 
                subcontrol-origin: margin; 
                left: 15px; 
                padding: 0 8px; 
            }
            QPlainTextEdit, QTextEdit { 
                background-color: #363638; 
                color: #FFFFFF; 
                border: none; 
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            }
            QPushButton { 
                background-color: #0A84FF; 
                color: #FFFFFF; 
                border-radius: 6px; 
                padding: 8px; 
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover { 
                background-color: #0070D8; 
            }
            QPushButton:pressed {
                background-color: #005CB8;
            }
            QPushButton:disabled { 
                background-color: #3A3A3C; 
                color: #8E8E93; 
            }
            QComboBox { 
                background-color: #363638; 
                color: #FFFFFF; 
                border: none; 
                border-radius: 6px; 
                padding: 5px 10px; 
                font-size: 13px;
                min-height: 25px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QScrollArea, QScrollBar {
                background-color: #2C2C2E;
                border: none;
            }
            QScrollBar:vertical {
                width: 8px;
                background: #2C2C2E;
            }
            QScrollBar::handle:vertical {
                background: #5A5A5E;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::add-line, QScrollBar::sub-line {
                height: 0px;
            }
            
            /* 替换示例面板样式 */
            #examplesTitleContainer {
                background-color: #2C2C2E;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                padding: 5px 0;
            }
            #examplesTitle {
                color: #FFFFFF;
                font-size: 18px;
                font-weight: bold;
                letter-spacing: 0.5px;
            }
            #examplesSeparator {
                background-color: #4A4A4C;
                height: 2px;
            }
            #examplesScrollArea {
                background-color: #252528;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            }
            
            /* 信息卡片样式 */
            #examplesInfoCard, #examplesNoteCard {
                background-color: #323235;
                border-radius: 8px;
                margin-bottom: 15px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
            }
            #examplesInfoTitle, #examplesNoteTitle {
                color: #0A84FF;
                font-size: 15px;
                font-weight: bold;
                margin-bottom: 5px;
            }
            #examplesInfoContent {
                color: #FFFFFF;
                font-size: 14px;
                line-height: 1.4;
            }
            #examplesNoteContent {
                color: #FFB340;
                font-size: 14px;
                line-height: 1.4;
            }
            
            /* 替换组标题样式 */
            #examplesGroupHeader {
                background-color: #3A3A42;
                border-radius: 6px;
                margin-top: 15px;
                margin-bottom: 10px;
                padding: 10px 0;
            }
            #examplesGroupTitle {
                color: #30D158;
                font-size: 15px;
                font-weight: bold;
                letter-spacing: 0.3px;
            }
            #examplesGroupSeparator {
                background-color: #4A4A4C;
                height: 1px;
                margin: 20px 0;
            }
            
            /* 语言示例项样式 */
            #languageExampleItem {
                background-color: #323235;
                border-radius: 10px;
                border: 1px solid #444446;
                box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
                margin-bottom: 10px;
                transition: transform 0.2s, box-shadow 0.2s;
                max-width: 800px;
            }
            #languageExampleItem:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            }
            #exampleContentArea {
                padding: 0 5px;
                width: 100%;
            }
            #replacedPartContainer {
                margin-bottom: 8px;
                background-color: rgba(255, 159, 10, 0.1);
                border-radius: 5px;
                padding: 5px 8px;
            }
            #replacedPartLabel {
                color: #FF9F0A;
                font-size: 13px;
                font-weight: bold;
            }
            #exampleSectionLabel {
                color: #AEAEB2;
                font-size: 12px;
                margin-bottom: 5px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            #exampleSentence {
                color: #FFFFFF;
                font-size: 16px;
                font-weight: 500;
                line-height: 1.7;
                padding: 10px 12px;
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 6px;
                margin-bottom: 5px;
                width: 100%;
                overflow-wrap: break-word;
                word-break: normal;
                text-align: left;
            }
            #exampleTranslation {
                color: #E5E5EA;
                font-size: 14px;
                line-height: 1.7;
                padding: 10px 12px;
                background-color: rgba(255, 255, 255, 0.03);
                border-radius: 6px;
                margin-bottom: 5px;
                width: 100%;
                overflow-wrap: break-word;
                word-break: normal;
                text-align: left;
            }
            #exampleGrammarNote {
                color: #64D2FF;
                font-size: 13px;
                line-height: 1.7;
                padding: 10px 12px;
                background-color: rgba(100, 210, 255, 0.08);
                border-radius: 6px;
                width: 100%;
                overflow-wrap: break-word;
                word-break: normal;
                text-align: left;
            }
            #exampleButtonArea {
                margin-top: 10px;
                display: flex;
                justify-content: flex-end;
            }
            #addToAnkiButton {
                background-color: #0A84FF;
                color: #FFFFFF;
                font-weight: bold;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 13px;
                max-width: 140px;
            }
            #addToAnkiButton:hover {
                background-color: #0070D8;
            }
            #addToAnkiButton:pressed {
                background-color: #005BB5;
            }
            /* 声音按钮样式 */
            #soundButton {
                background-color: #555559;
                color: #FFFFFF;
                border-radius: 4px;
                font-size: 12px;
                padding: 2px 8px;
                min-height: 20px;
            }
            #soundButton:hover {
                background-color: #64646A;
            }
            
            /* 日语专用样式增强 */
            .jp-text {
                font-family: "Hiragino Sans", "Meiryo", "MS Gothic", sans-serif;
                line-height: 1.8;
                letter-spacing: 0.03em;
            }
        """)
        else:
            # 浅色模式
            widget.setStyleSheet("""
            QDialog { 
                background-color: #F2F2F7; 
                color: #000000; 
            }
            QLabel { 
                color: #000000; 
                font-size: 13px;
            }
            QGroupBox { 
                background-color: #FFFFFF; 
                border-radius: 10px; 
                color: #000000; 
                font-size: 14px;
                padding-top: 15px; 
                margin-top: 15px; 
                border: 1px solid #E5E5EA;
            }
            QGroupBox::title { 
                subcontrol-origin: margin; 
                left: 15px; 
                padding: 0 8px; 
            }
            QPlainTextEdit, QTextEdit { 
                background-color: #FFFFFF; 
                color: #000000; 
                border: 1px solid #E5E5EA; 
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            }
            QPushButton { 
                background-color: #007AFF; 
                color: #FFFFFF; 
                border-radius: 6px; 
                padding: 8px; 
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover { 
                background-color: #0062CC; 
            }
            QPushButton:pressed {
                background-color: #0051A8;
            }
            QPushButton:disabled { 
                background-color: #E5E5EA; 
                color: #8E8E93; 
            }
            QComboBox { 
                background-color: #FFFFFF; 
                color: #000000; 
                border: 1px solid #E5E5EA; 
                border-radius: 6px; 
                padding: 5px 10px; 
                font-size: 13px;
                min-height: 25px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QScrollArea, QScrollBar {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                width: 8px;
                background: transparent;
            }
            QScrollBar::handle:vertical {
                background: #C7C7CC;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::add-line, QScrollBar::sub-line {
                height: 0px;
            }
            
            /* 替换示例面板样式 */
            #examplesTitleContainer {
                background-color: #F5F5F7;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                padding: 5px 0;
                border-bottom: 1px solid #D1D1D6;
            }
            #examplesTitle {
                color: #111111;
                font-size: 18px;
                font-weight: bold;
                letter-spacing: 0.5px;
            }
            #examplesSeparator {
                background-color: #D1D1D6;
                height: 2px;
            }
            #examplesScrollArea {
                background-color: #FCFCFC;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            }
            
            /* 信息卡片样式 */
            #examplesInfoCard, #examplesNoteCard {
                background-color: #F0F0F5;
                border-radius: 8px;
                margin-bottom: 15px;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                border: 1px solid #E5E5EA;
            }
            #examplesInfoTitle, #examplesNoteTitle {
                color: #007AFF;
                font-size: 15px;
                font-weight: bold;
                margin-bottom: 5px;
            }
            #examplesInfoContent {
                color: #111111;
                font-size: 14px;
                line-height: 1.4;
            }
            #examplesNoteContent {
                color: #FF9500;
                font-size: 14px;
                line-height: 1.4;
            }
            
            /* 替换组标题样式 */
            #examplesGroupHeader {
                background-color: #E9E9F0;
                border-radius: 6px;
                margin-top: 15px;
                margin-bottom: 10px;
                padding: 10px 0;
            }
            #examplesGroupTitle {
                color: #34C759;
                font-size: 15px;
                font-weight: bold;
                letter-spacing: 0.3px;
            }
            #examplesGroupSeparator {
                background-color: #D1D1D6;
                height: 1px;
                margin: 20px 0;
            }
            
            /* 语言示例项样式 */
            #languageExampleItem {
                background-color: #FFFFFF;
                border-radius: 10px;
                border: 1px solid #E5E5EA;
                box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
                margin-bottom: 10px;
                transition: transform 0.2s, box-shadow 0.2s;
                max-width: 800px;
            }
            #languageExampleItem:hover {
                transform: translateY(-2px);
                box-shadow: 0 3px 7px rgba(0, 0, 0, 0.12);
            }
            #exampleContentArea {
                padding: 0 5px;
                width: 100%;
            }
            #replacedPartContainer {
                margin-bottom: 8px;
                background-color: rgba(255, 149, 0, 0.1);
                border-radius: 5px;
                padding: 5px 8px;
            }
            #replacedPartLabel {
                color: #FF9500;
                font-size: 13px;
                font-weight: bold;
            }
            #exampleSectionLabel {
                color: #8E8E93;
                font-size: 12px;
                margin-bottom: 5px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            #exampleSentence {
                color: #111111;
                font-size: 16px;
                font-weight: 500;
                line-height: 1.7;
                padding: 10px 12px;
                background-color: #F8F8FA;
                border-radius: 6px;
                margin-bottom: 5px;
                width: 100%;
                overflow-wrap: break-word;
                word-break: normal;
                text-align: left;
            }
            #exampleTranslation {
                color: #484848;
                font-size: 14px;
                line-height: 1.7;
                padding: 10px 12px;
                background-color: #F9F9FB;
                border-radius: 6px;
                margin-bottom: 5px;
                width: 100%;
                overflow-wrap: break-word;
                word-break: normal;
                text-align: left;
            }
            #exampleGrammarNote {
                color: #0070C9;
                font-size: 13px;
                line-height: 1.7;
                padding: 10px 12px;
                background-color: rgba(0, 122, 255, 0.05);
                border-radius: 6px;
                width: 100%;
                overflow-wrap: break-word;
                word-break: normal;
                text-align: left;
            }
            #exampleButtonArea {
                margin-top: 10px;
                display: flex;
                justify-content: flex-end;
            }
            #addToAnkiButton {
                background-color: #007AFF;
                color: #FFFFFF;
                font-weight: bold;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 13px;
                max-width: 140px;
            }
            #addToAnkiButton:hover {
                background-color: #0062CC;
            }
            #addToAnkiButton:pressed {
                background-color: #0051A8;
            }
            /* 声音按钮样式 - 浅色模式 */
            #soundButton {
                background-color: #D1D1D6;
                color: #000000;
                border-radius: 4px;
                font-size: 12px;
                padding: 2px 8px;
                min-height: 20px;
            }
            #soundButton:hover {
                background-color: #C7C7CC;
            }
            
            /* 日语专用样式增强 - 浅色模式 */
            .jp-text {
                font-family: "Hiragino Sans", "Meiryo", "MS Gothic", sans-serif;
                line-height: 1.8;
                letter-spacing: 0.03em;
            }
        """)
    except:
        # 如果获取主题失败，使用默认苹果浅色样式
        pass 