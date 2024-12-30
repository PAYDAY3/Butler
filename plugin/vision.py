import base64
import contextlib
import io
import os
import tempfile

from PIL import Image

from ...utils.lazy_import import lazy_import
from ..utils.computer_vision import pytesseract_get_text

class Vision:
    def __init__(self, computer):
        self.computer = computer
        self.model = None  # Will load upon first use
        self.tokenizer = None  # Will load upon first use
        self.easyocr = None

    def load(self, load_moondream=True, load_easyocr=True):
        with contextlib.redirect_stdout(
            open(os.devnull, "w")
        ), contextlib.redirect_stderr(open(os.devnull, "w")):
            if self.easyocr is None and load_easyocr:
                import easyocr
                self.easyocr = easyocr.Reader(["en"])

            if self.model is None and load_moondream:
                import transformers  # Wait until we use it. Transformers can't be lazy loaded for some reason!

                os.environ["TOKENIZERS_PARALLELISM"] = "false"

                if self.computer.debug:
                    print("Open Interpreter 将使用 Moondream (小型视觉模型) 来描述图像给语言模型。设置 `interpreter.llm.vision_renderer = None` 来禁用此行为。")
                    print("或者，您可以使用支持视觉的 LLM 并设置 `interpreter.llm.supports_vision = True`。")
                model_id = "vikhyatk/moondream2"
                revision = "2024-04-02"
                print("正在加载模型")

                self.model = transformers.AutoModelForCausalLM.from_pretrained(
                    model_id, trust_remote_code=True, revision=revision
                )
                self.tokenizer = transformers.AutoTokenizer.from_pretrained(
                    model_id, revision=revision
                )
                return True

    def ocr(self, base_64=None, path=None, lmc=None, pil_image=None):
        """
        获取图像的 OCR 结果。
        """
        if lmc:
            if "base64" in lmc["format"]:
                img_data = base64.b64decode(lmc["content"])
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                    temp_file.write(img_data)
                    temp_file_path = temp_file.name
                path = temp_file_path
            elif lmc["format"] == "path":
                path = lmc["content"]
        elif base_64:
            img_data = base64.b64decode(base_64)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                temp_file.write(img_data)
                temp_file_path = temp_file.name
            path = temp_file_path
        elif path:
            pass
        elif pil_image:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                pil_image.save(temp_file, format="PNG")
                temp_file_path = temp_file.name
            path = temp_file_path

        try:
            if not self.easyocr:
                self.load(load_moondream=False)
            result = self.easyocr.readtext(path)
            text = " ".join([item[1] for item in result])
            return text.strip()
        except ImportError:
            print("要使用本地视觉，请运行 `pip install 'open-interpreter[local]'`。")
            return ""

    def query(self, query="描述这张图像。如果有任何文字，也请告诉我。", base_64=None, path=None, lmc=None, pil_image=None):
        """
        使用 Moondream 对图像进行查询（图像可以是 base64、路径或 lmc 消息）。
        """
        if self.model is None and self.tokenizer is None:
            try:
                success = self.load(load_easyocr=False)
            except ImportError:
                print("要使用本地视觉，请运行 `pip install 'open-interpreter[local]'`。")
                return ""
            if not success:
                return ""

        if lmc:
            if "base64" in lmc["format"]:
                img_data = base64.b64decode(lmc["content"])
                img = Image.open(io.BytesIO(img_data))
            elif lmc["format"] == "path":
                image_path = lmc["content"]
                img = Image.open(image_path)
        elif base_64:
            img_data = base64.b64decode(base_64)
            img = Image.open(io.BytesIO(img_data))
        elif path:
            img = Image.open(path)
        elif pil_image:
            img = pil_image

        with contextlib.redirect_stdout(open(os.devnull, "w")):
            enc_image = self.model.encode_image(img)
            answer = self.model.answer_question(
                enc_image, query, self.tokenizer, max_length=400
            )

        return answer

    def save_image(self, image_content, output_path):
        """
        将图像内容保存到指定路径。
        """
        img_data = base64.b64decode(image_content)
        with open(output_path, "wb") as f:
            f.write(img_data)
        print(f"图像已保存到 {output_path}")

    def resize_image(self, input_path, output_path, size):
        """
        调整图像大小。
        """
        img = Image.open(input_path)
        img = img.resize(size, Image.ANTIALIAS)
        img.save(output_path)
        print(f"图像已调整大小并保存到 {output_path}")
