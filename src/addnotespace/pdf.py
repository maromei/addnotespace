from pathlib import Path
from decimal import Decimal

import PyPDF2 as pypdf


def add_margin(
    pdf_path: str | Path,
    pdf_out_path: str | Path,
    top_mod: float,
    right_mod: float,
    bot_mod: float,
    left_mod: float,
):
    """
    Adds the margins to a pdf file.

    Args:
        pdf_path (str | Path): PDF which should be modified
        pdf_out_path (str | Path): output PDF
        top_mod (int): fraction of height to add to top of pdf slides
        right_mod (int): fraction of width to add to right of pdf slides
        bot_mod (int): fraction of height to add to bot of pdf slides
        left_mod (int): fraction of width to add to left of pdf slides
    """

    writer = pypdf.PdfWriter()

    with open(pdf_path, "rb") as f:

        pdf = pypdf.PdfReader(f, strict=False)
        nmbr_pages = len(pdf.pages)

        for i in range(nmbr_pages):

            top_margin = pdf.pages[i].mediabox.width * Decimal(top_mod)
            right_margin = pdf.pages[i].mediabox.height * Decimal(right_mod)
            bot_margin = pdf.pages[i].mediabox.width * Decimal(bot_mod)
            left_margin = pdf.pages[i].mediabox.height * Decimal(left_mod)

            page = pdf.pages[i]

            new_width = page.mediabox.width + right_margin + left_margin
            new_height = page.mediabox.height + top_margin + bot_margin

            new_page = pypdf.PageObject.create_blank_page(
                width=new_width, height=new_height
            )
            new_page.merge_page(page)

            transform = (
                pypdf.Transformation()
                .scale(1)
                .translate(float(left_margin), float(bot_margin))
            )
            new_page.add_transformation(transform)

            writer.add_page(new_page)

        # input file has to be accessible when writing!
        with open(pdf_out_path, "wb+") as fo:
            writer.write(fo)
