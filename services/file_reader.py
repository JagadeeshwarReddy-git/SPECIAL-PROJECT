
import io
import json
from pathlib import Path

import pandas as pd


SUPPORTED_EXTENSIONS = [
    "csv",
    "pdf",
    "docx",
    "doc",
    "xlsx",
    "xls",
    "txt",
    "json",
]


def read_uploaded_file(uploaded_file):
    """
    Read supported document and data files.

    Returns:
        A pandas DataFrame containing extracted content.
    """

    filename = uploaded_file.name
    extension = Path(filename).suffix.lower()
    raw = uploaded_file.getvalue()

    if not raw:
        raise ValueError("The uploaded file is empty.")

    # ------------------------------------------------------
    # CSV
    # ------------------------------------------------------
    if extension == ".csv":
        last_error = None

        for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
            try:
                return pd.read_csv(
                    io.BytesIO(raw),
                    encoding=encoding,
                    sep=None,
                    engine="python",
                )
            except Exception as exc:
                last_error = exc

        raise ValueError(f"Could not read CSV: {last_error}")

    # ------------------------------------------------------
    # EXCEL
    # ------------------------------------------------------
    if extension in (".xlsx", ".xls"):
        sheets = pd.read_excel(
            io.BytesIO(raw),
            sheet_name=None,
        )

        frames = []

        for sheet_name, frame in sheets.items():
            if frame.empty:
                continue

            frame = frame.copy()
            frame.insert(0, "source_sheet", sheet_name)
            frames.append(frame)

        if not frames:
            return pd.DataFrame()

        return pd.concat(
            frames,
            ignore_index=True,
            sort=False,
        )

    # ------------------------------------------------------
    # PDF
    # ------------------------------------------------------
    if extension == ".pdf":
        try:
            import pymupdf

            document = pymupdf.open(stream=raw, filetype="pdf")

            pages = []

            for page_number, page in enumerate(document, start=1):
                page_text = page.get_text("text").strip()

                if page_text:
                    pages.append({
                        "page": page_number,
                        "text": page_text,
                    })

            document.close()

            if not pages:
                raise ValueError(
                    "No selectable text was found in this PDF. "
                    "It may be scanned; OCR is needed to extract its text."
                )

            return pd.DataFrame(pages)

        except ImportError:
            raise ValueError(
                "PDF support is not installed. Run: "
                "python -m pip install pymupdf"
            )

    # ------------------------------------------------------
    # WORD DOCX
    # ------------------------------------------------------
    if extension == ".docx":
        try:
            from docx import Document

            document = Document(io.BytesIO(raw))

            parts = []

            for paragraph in document.paragraphs:
                if paragraph.text.strip():
                    parts.append(paragraph.text.strip())

            for table_number, table in enumerate(
                document.tables,
                start=1,
            ):
                for row in table.rows:
                    values = [
                        cell.text.strip()
                        for cell in row.cells
                    ]

                    if any(values):
                        parts.append(
                            f"[Table {table_number}] "
                            + " | ".join(values)
                        )

            if not parts:
                raise ValueError(
                    "No readable text was found in this Word document."
                )

            return pd.DataFrame({
                "text": parts,
            })

        except ImportError:
            raise ValueError(
                "Word support is not installed. Run: "
                "python -m pip install python-docx"
            )

    # ------------------------------------------------------
    # LEGACY WORD DOC
    # ------------------------------------------------------
    if extension == ".doc":
        try:
            import textract

            text = textract.process(
                io.BytesIO(raw),
                extension="doc",
            ).decode("utf-8", errors="replace").strip()

            if not text:
                raise ValueError("No readable text was found in this DOC file.")

            return pd.DataFrame({
                "text": [text],
            })

        except ImportError:
            raise ValueError(
                "Legacy .doc support requires textract and its system "
                "dependencies. For the easiest setup, save the document "
                "as .docx in Microsoft Word and upload it again."
            )

    # ------------------------------------------------------
    # PLAIN TEXT
    # ------------------------------------------------------
    if extension == ".txt":
        text = raw.decode("utf-8-sig", errors="replace").strip()

        if not text:
            raise ValueError("The text file contains no readable content.")

        return pd.DataFrame({
            "text": [text],
        })

    # ------------------------------------------------------
    # JSON
    # ------------------------------------------------------
    if extension == ".json":
        try:
            data = json.loads(raw.decode("utf-8-sig"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"Could not read JSON: {exc}")

        if isinstance(data, list):
            return pd.json_normalize(data)

        if isinstance(data, dict):
            return pd.json_normalize(data)

        return pd.DataFrame({
            "text": [str(data)],
        })

    raise ValueError(
        f"Unsupported file format: {extension}. "
        f"Supported formats: {', '.join(SUPPORTED_EXTENSIONS)}"
    )
