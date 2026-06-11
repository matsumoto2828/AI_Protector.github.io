import io
from flask import Flask, request, render_template_string, send_file
import cv2
import numpy as np

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 最大16MB

# HTML/CSS/JS テンプレート (1ファイルで完結するようにインラインで定義)
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-2861247104118830"
     crossorigin="anonymous"></script>
    <meta name="google-site-verification" content="N2BcjtShs4wEitWTlkXRau1uwXrpXuWCKlWsebaySAc" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Fractal Protector - AI学習妨害線画ツール</title>
    <style>
        :root {
            --primary-color: #4a6fa5;
            --primary-hover: #3b5984;
            --bg-color: #f4f6f9;
            --card-bg: #ffffff;
            --text-color: #333333;
            --accent-color: #ff6b6b;
        }

        body {
            font-family: 'Helvetica Neue', Arial, 'Hiragino Kaku Gothic ProN',
            sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }

        header {
            background-color: var(--card-bg);
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 15px 20px;
            text-align: center;
        }

        header h1 {
            margin: 0;
            font-size: 24px;
            color: var(--primary-color);
        }

        header p {
            margin: 5px 0 0 0;
            font-size: 14px;
            color: #666;
        }

        .container {
            max-width: 1000px;
            margin: 20px auto;
            padding: 0 20px;
            display: grid;
            grid-template-columns: 1fr 250px; /* メインコンテンツとサイドバー広告 */
            gap: 20px;
            flex: 1;
        }

        @media (max-width: 768px) {
            .container {
                grid-template-columns: 1fr;
            }
            .sidebar-ad {
                display: none; /* スマホではサイドバー広告を非表示、または下部に移動 */
            }
        }

        .main-content {
            background-color: var(--card-bg);
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            padding: 30px;
            text-align: center;
        }

        /* 広告枠のスタイル */
        .ad-space {
            background-color: #eaeaea;
            border: 1px dashed #bbb;
            color: #777;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
            border-radius: 4px;
            margin-bottom: 20px;
        }

        .top-ad {
            width: 100%;
            height: 90px;
            margin: 10px auto;
            max-width: 728px;
        }

        .sidebar-ad {
            height: 600px;
            position: sticky;
            top: 20px;
        }

        /* ドラッグ＆ドロップエリア */
        .drop-zone {
            border: 3px dashed #b4c6e7;
            border-radius: 8px;
            padding: 50px 20px;
            cursor: pointer;
            transition: background-color 0.3s, border-color 0.3s;
            background-color: #fdfdfd;
            margin-bottom: 20px;
        }

        .drop-zone:hover, .drop-zone.dragover {
            background-color: #f0f4f8;
            border-color: var(--primary-color);
        }

        .drop-zone p {
            margin: 10px 0 0 0;
            font-size: 16px;
            color: #555;
        }

        .drop-zone-icon {
            font-size: 48px;
            color: var(--primary-color);
        }

        #file-input {
            display: none;
        }

        /* プレビューエリア */
        .preview-container {
            display: none;
            margin-top: 20px;
            margin-bottom: 20px;
        }

        .preview-image {
            max-width: 100%;
            max-height: 300px;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        /* ボタン */
        .btn {
            background-color: var(--primary-color);
            color: white;
            border: none;
            padding: 12px 30px;
            font-size: 16px;
            font-weight: bold;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.2s;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }

        .btn:hover {
            background-color: var(--primary-hover);
        }

        .btn:disabled {
            background-color: #ccc;
            cursor: not-allowed;
        }

        .btn-download {
            background-color: #28a745;
            display: none;
            margin-top: 15px;
            text-decoration: none;
        }

        .btn-download:hover {
            background-color: #218838;
        }

        /* ローディング表示 */
        .spinner {
            display: none;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top-color: white;
            animation: spin 1s ease-in-out infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        footer {
            text-align: center;
            padding: 20px;
            font-size: 12px;
            color: #888;
            background-color: #fff;
            margin-top: auto;
            border-top: 1px solid #e0e0e0;
        }
    </style>
</head>
<body>

    <header>
        <h1>🛡️ AI Fractal Protector</h1>
        <p>3層フラクタル構造ノイズによる、人間には美しくAIには壊れて見える画像学習妨害ツール</p>
        <!-- 上部バナー広告枠 -->
        <div class="ad-space top-auto top-ad">
            <!-- Google AdSense などの広告コードをここに配置 -->
            スポンサー広告 (728x90)
        </div>
    </header>

    <div class="container">
        <!-- メインコンテンツ -->
        <div class="main-content">
            <form id="upload-form">
                <div class="drop-zone" id="drop-zone">
                    <div class="drop-zone-icon">📥</div>
                    <p>ここに画像をドラッグ＆ドロップ、またはクリックしてファイルを選択</p>
                    <p style="font-size: 12px; color: #888;">対応形式: JPG,
                    PNG (最大16MB)</p>
                    <input type="file" id="file-input" accept="image/jpeg,
                    image/png">
                </div>

                <div class="preview-container" id="preview-container">
                    <h3>インポートされた画像プレビュー</h3>
                    <img src="" alt="Preview" class="preview-image
                    "id="img-preview">
                </div>

                <button type="button" class="btn" id="process-btn" disabled>
                    <span class="spinner" id="spinner"></span>
                    <span id="btn-text">フラクタルプロテクト実行</span>
                </button>
            </form>

            <a href="#" class="btn btn-download" id="download-btn"
            download="protected_image">
                📥 保護済み画像をダウンロード
            </a>
        </div>

        <!-- サイドバー広告枠 -->
        <div class="sidebar-ad ad-space">
            <!-- Google AdSense などのサイドバー広告コードをここに配置 -->
            スポンサー広告 (250x600)
        </div>
    </div>

    <footer>
        <p>&copy; 2026 AI Fractal Protector. All rights reserved.
        画像データはサーバーに保存されず、安全に処理されます。</p>
    </footer>

    <script>
        const dropZone = document.getElementById('drop-zone');
        const fileInput = document.getElementById('file-input');
        const processBtn = document.getElementById('process-btn');
        const downloadBtn = document.getElementById('download-btn');
        const previewContainer = document.getElementById('preview-container');
        const imgPreview = document.getElementById('img-preview');
        const spinner = document.getElementById('spinner');
        const btnText = document.getElementById('btn-text');

        let selectedFile = null;

        // ドラッグ＆ドロップイベント
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                dropZone.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                dropZone.classList.remove('dragover');
            }, false);
        });

        dropZone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length > 0) {
                handleFile(files[0]);
            }
        });

        dropZone.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFile(e.target.files[0]);
            }
        });

        function handleFile(file) {
            if (file.type === 'image/jpeg' || file.type === 'image/png') {
                selectedFile = file;
                processBtn.disabled = false;
                downloadBtn.style.display = 'none';

                // プレビュー表示
                const reader = new FileReader();
                reader.readAsDataURL(file);
                reader.onloadend = function() {
                    imgPreview.src = reader.result;
                    previewContainer.style.display = 'block';
                }
            } else {
                alert('JPGまたはPNG形式の画像を選択してください。');
            }
        }

        // 実行処理（非同期通信）
        processBtn.addEventListener('click', async () => {
            if (!selectedFile) return;

            // ローディング状態へ移行
            processBtn.disabled = true;
            spinner.style.display = 'inline-block';
            btnText.textContent = '処理中...';

            const formData = new FormData();
            formData.append('image', selectedFile);

            try {
                const response = await fetch('/process', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) throw new Error('画像処理に失敗しました。');

                // 処理後画像をBlobとして取得
                const blob = await response.blob();
                const downloadUrl = URL.createObjectURL(blob);
                // ダウンロードボタンの設定
                downloadBtn.href = downloadUrl;
                // 元のファイル拡張子を維持
                const extension = selectedFile.type === 'image/png' ? 'png' :
                'jpg';
                downloadBtn.download = `protected_${Date.now()}.${extension}`;
                downloadBtn.style.display = 'inline-flex';
                btnText.textContent = '処理完了！';
            } catch (error) {
                alert(error.message);
                btnText.textContent = 'エラーが発生しました';
            } finally {
                spinner.style.display = 'none';
                processBtn.disabled = false;
            }
        });
    </script>
</body>
</html>
'''
import traceback

# 3層フラクタル処理アルゴリズム (Python / OpenCV) - 同系色・高彩度オーバーレイ版
def apply_three_layer_fractal(image_bytes, ext):
    try:
        # バイト列から画像をデコード
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
        
        if img is None:
            raise ValueError("画像のデコードに失敗しました。")

        # 1. オリジナルの色情報と透過情報を確保
        has_alpha = False
        if len(img.shape) == 3 and img.shape[2] == 4:
            color_img = img[:, :, :3].copy()
            alpha_channel = img[:, :, 3].copy()
            has_alpha = True
        elif len(img.shape) == 3:
            color_img = img.copy()
        else:
            color_img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

        gray = cv2.cvtColor(color_img, cv2.COLOR_BGR2GRAY)

        # 2. 輪郭（エッジ）の抽出
        edges = cv2.Canny(gray, 50, 150)
        rows, cols = edges.shape

        # --- 1. ミクロ層（高周波ノイズ） ---
        noise_micro = np.random.randint(0, 2, edges.shape, dtype=np.uint8) * 255
        edges_micro = np.where(edges > 0, np.bitwise_xor(edges, noise_micro), edges).astype(np.uint8)

        # --- 2. ミドル層（輪郭のランダムなズレ） ---
        edges_mid = edges_micro.copy()
        block_size = 4
        for y in range(0, rows - block_size, block_size):
            for x in range(0, cols - block_size, block_size):
                if np.any(edges[y:y+block_size, x:x+block_size] > 0):
                    shift_x = np.random.randint(-3, 4)
                    shift_y = np.random.randint(-3, 4)
                    M = np.float32([[1, 0, shift_x], [0, 1, shift_y]])
                    block = edges_mid[y:y+block_size, x:x+block_size]
                    edges_mid[y:y+block_size, x:x+block_size] = cv2.warpAffine(
                        block, M, (block_size, block_size), borderMode=cv2.BORDER_REPLICATE
                    )

        # --- 3. マクロ層（空間の緩やかなうねり） ---
        edges_macro = np.zeros_like(edges_mid)
        for i in range(rows):
            offset_x = int(3.0 * np.sin(2 * np.pi * i / 150.0))
            edges_macro[i, :] = np.roll(edges_mid[i, :], offset_x)

        # --- 4. 元のカラー画像への合成（彩度ブースト処理） ---
        # BGRからHSV（色相・彩度・明度）カラースペースに変換
        hsv_img = cv2.cvtColor(color_img, cv2.COLOR_BGR2HSV)
        
        # フラクタル線画のマスク（線がある部分をTrueにする）
        mask = edges_macro > 0
        
        # Sチャンネル（彩度）とVチャンネル（明度）を操作するために型を大きくする（計算時のオーバーフロー防止）
        s_channel = hsv_img[:, :, 1].astype(np.int16)
        v_channel = hsv_img[:, :, 2].astype(np.int16)

        # 線画部分の「彩度」を大幅に上げ（元の2倍＋固定値）、最大値(255)で抑える
        s_channel[mask] = np.clip(s_channel[mask] * 2 + 100, 0, 255)
        
        # 白や黒など「彩度がない部分」でも線が見えるように、少しだけ「明度」を下げる（少し濃くする）
        v_channel[mask] = np.clip(v_channel[mask] - 40, 0, 255)

        # 変更したチャンネルをHSV画像に戻す
        hsv_img[:, :, 1] = s_channel.astype(np.uint8)
        hsv_img[:, :, 2] = v_channel.astype(np.uint8)

        # HSVからBGR（元のカラースペース）に戻す
        result_color = cv2.cvtColor(hsv_img, cv2.COLOR_HSV2BGR)

        # アルファチャンネル（背景透過）があった場合は元に戻す
        if has_alpha:
            res_img = cv2.merge([result_color[:, :, 0], result_color[:, :, 1], result_color[:, :, 2], alpha_channel])
        else:
            res_img = result_color

        # エンコードして返す
        success, encoded_img = cv2.imencode(f'.{ext}', res_img)
        if not success:
             raise ValueError("画像のエンコードに失敗しました。")

        return encoded_img.tobytes(), None

    except Exception as e:
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        print("画像処理エラー:", error_msg)
        return None, str(e)


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/process', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return '画像ファイルが見つかりません', 400
    
    file = request.files['image']
    if file.filename == '':
        return 'ファイルが選択されていません', 400

    if file:
        filename = file.filename.lower()
        if filename.endswith('.png'):
            ext = 'png'
            mimetype = 'image/png'
        else:
            ext = 'jpg'
            mimetype = 'image/jpeg'

        image_bytes = file.read()
        # 修正：エラーメッセージも受け取るように変更
        processed_bytes, error_msg = apply_three_layer_fractal(image_bytes, ext)

        if processed_bytes is None:
            # ブラウザ側にエラーの理由を直接返す
            return f'画像処理エラー: {error_msg}', 500

        return send_file(
            io.BytesIO(processed_bytes),
            mimetype=mimetype,
            as_attachment=True,
            download_name=f'protected.{ext}'
        )

if __name__ == '__main__':
    print("AI Fractal Protector サーバーを起動します。")
    print("ブラウザで http://127.0.0.1:5000/ を開いてください。")
    app.run(debug=True, port=5000)
