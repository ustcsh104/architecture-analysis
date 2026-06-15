"""
Word 转 PDF 工具
支持单个文件转换和批量转换
依赖: pip install docx2pdf
"""

import sys
import os
from pathlib import Path

try:
    from docx2pdf import convert
except ImportError:
    print("缺少依赖，请先安装: pip install docx2pdf")
    sys.exit(1)


def word_to_pdf(input_path: str, output_path: str = None) -> str:
    """
    将 Word 文件转换为 PDF

    Args:
        input_path: Word 文件路径 (.doc 或 .docx)
        output_path: PDF 输出路径，默认与源文件同目录同名

    Returns:
        生成的 PDF 文件路径
    """
    input_path = os.path.abspath(input_path)
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"文件不存在: {input_path}")

    ext = os.path.splitext(input_path)[1].lower()
    if ext not in (".doc", ".docx"):
        raise ValueError(f"仅支持 .doc/.docx 文件，收到: {ext}")

    if output_path is None:
        output_path = os.path.splitext(input_path)[0] + ".pdf"
    else:
        output_path = os.path.abspath(output_path)

    convert(input_path, output_path)
    print(f"转换成功: {input_path} -> {output_path}")
    return output_path


def batch_convert(folder_path: str) -> list:
    """
    批量转换文件夹中的所有 Word 文件为 PDF

    Args:
        folder_path: 包含 Word 文件的文件夹路径

    Returns:
        生成的 PDF 文件路径列表
    """
    folder_path = os.path.abspath(folder_path)
    if not os.path.isdir(folder_path):
        raise NotADirectoryError(f"文件夹不存在: {folder_path}")

    results = []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith((".doc", ".docx")):
            input_file = os.path.join(folder_path, filename)
            try:
                pdf_path = word_to_pdf(input_file)
                results.append(pdf_path)
            except Exception as e:
                print(f"转换失败 [{filename}]: {e}")

    print(f"\n批量转换完成，共 {len(results)} 个文件")
    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  单文件转换: python word2pdf.py <word文件路径> [pdf输出路径]")
        print("  批量转换:   python word2pdf.py <文件夹路径>")
        print("\n示例:")
        print("  python word2pdf.py document.docx")
        print("  python word2pdf.py document.docx output.pdf")
        print("  python word2pdf.py ./docs")
        sys.exit(0)

    target = sys.argv[1]

    if os.path.isdir(target):
        batch_convert(target)
    else:
        output = sys.argv[2] if len(sys.argv) >= 3 else None
        word_to_pdf(target, output)
