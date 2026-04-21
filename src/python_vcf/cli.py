import typer
from typing import Annotated
from enum import Enum
from python_vcf.rfc2426 import (
    VCard3,
    Name,
    Telephone,
    Address,
    AdrType,
    Organization,
    Email,
    EmailType,
    TelType,
    Photo,
)
from python_vcf.rfc6350 import VCard4
import qrcodegen
import xml.etree.ElementTree as ET
from pathlib import Path

app = typer.Typer()


class Version(str, Enum):
    v3 = "3.0"
    v4 = "4.0"


VERSION = {"3.0": VCard3, "4.0": VCard4}


def qr_to_svg_str(qr, scale=10, border=4) -> str:
    """
    Generates an SVG string from a QR code.

    :param qr: QrCode instance (using qrcodegen.QrCode.encode_text(...))
    :param scale: scale for the size of final SVG.
    :param border: border number module around of the SVG.
    :return: SVG code as a string.
    """
    n = qr.get_size()  # taille du QR code en modules
    total_modules = n + border * 2
    width = total_modules * scale
    height = total_modules * scale

    svg_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0 0 {total_modules} {total_modules}" width="{width}" height="{height}">',
        '<rect width="100%" height="100%" fill="white"/>'
    ]

    for y in range(n):
        for x in range(n):
            if qr.get_module(x, y):
                svg_lines.append(
                    f'<rect x="{x + border}" y="{y + border}" width="1" height="1" fill="black"/>'
                )
    svg_lines.append("</svg>")
    return "\n".join(svg_lines)


def generate_qr_svg(text, scale=4, border=4):
    """
    Generate a QrCode from text.
    """
    qr = qrcodegen.QrCode.encode_text(text, qrcodegen.QrCode.Ecc.MEDIUM)
    svg_str = qr_to_svg_str(qr, scale, border)
    return svg_str


def embed_logo_in_svg(qr_svg_str, logo_svg_path, logo_scale=0.2):
    SVG_NS = "http://www.w3.org/2000/svg"
    ET.register_namespace("", SVG_NS)

    qr_svg = ET.fromstring(qr_svg_str)

    viewBox = qr_svg.get("viewBox")
    if viewBox is None:
        msg = "QR Code SVG does not contain any viewBox attribute."
        raise ValueError(msg)
    parts = viewBox.split()
    qr_size = float(parts[2])

    logo_tree = ET.parse(str(logo_svg_path))
    logo_svg = logo_tree.getroot()

    logo_viewBox = logo_svg.get("viewBox")
    if logo_viewBox:
        lv_parts = logo_viewBox.split()
        logo_width = float(lv_parts[2])
        logo_height = float(lv_parts[3])
    else:
        logo_width = float(logo_svg.get("width").replace("px", ""))
        logo_height = float(logo_svg.get("height").replace("px", ""))

    desired_logo_width = qr_size * logo_scale
    scale_factor = desired_logo_width / logo_width

    translate_x = (qr_size - (logo_width * scale_factor)) / 2
    translate_y = (qr_size - (logo_height * scale_factor)) / 2

    logo_group = ET.Element(f"{{{SVG_NS}}}g")
    logo_group.set(
        "transform", f"translate({translate_x},{translate_y}) scale({scale_factor})"
    )

    for elem in list(logo_svg):
        logo_group.append(elem)

    qr_svg.append(logo_group)

    return ET.tostring(qr_svg, encoding="unicode")


@app.command()
def create_vcard(
    country: Annotated[str, typer.Option("--country", "-co")] = "",
    city: Annotated[str, typer.Option("--city", "-ci")] = "",
    zip_code: Annotated[str, typer.Option("--zip-code", "-z")] = "",
    region: Annotated[str, typer.Option("--region", "-r")] = "",
    street: Annotated[str, typer.Option("--street", "-s")] = "",
    address_type: AdrType = AdrType.WORK,
    family_name: Annotated[str, typer.Option("--family-name", "-f", prompt=True)] = "",
    given_name: Annotated[str, typer.Option("--given-name", "-g", prompt=True)] = "",
    formatted_name: Annotated[str, typer.Option("--formatted-name", "-fn")] = "",
    additional_names: Annotated[
        list[str], typer.Option("--additional-name", "-a")
    ] = [],
    honorific_prefixes: Annotated[list[str], typer.Option("--prefix", "-p")] = [],
    honorific_suffixes: Annotated[list[str], typer.Option("--suffix", "-s")] = [],
    nickname: Annotated[str, typer.Option("--nickname", "-n")] = "",
    emails: Annotated[list[str], typer.Option("--email", "-e")] = [],
    phones: Annotated[list[str], typer.Option("--phone", "-ph")] = [],
    organization: Annotated[str, typer.Option("--organization", "-org")] = "",
    title: Annotated[str, typer.Option("--title", "-t")] = "",
    url: Annotated[list[str], typer.Option("--url", "-u")] = [],
    version: Annotated[Version, typer.Option()] = Version.v3,
    output_path: Annotated[str, typer.Option("--output", "-o")] = "./vcard.vcf",
):
    vcard_class = VERSION[version]
    name_obj = Name(
        family_name=family_name,
        given_name=given_name,
        additional_names=";".join(additional_names),
        honorific_prefixes=";".join(honorific_prefixes),
        honorific_suffixes=";".join(honorific_suffixes),
    )
    vcard = vcard_class(
        name=name_obj,
        nickname=nickname,
        formatted_name=formatted_name
        if formatted_name
        else f"{given_name} {family_name}"
        if not additional_names
        else f"{given_name} {' '.join(additional_names)} {family_name.upper()}",
        emails=[Email(value=email, types=[EmailType.INTERNET]) for email in emails],
        telephones=[Telephone(value=phone, types=[TelType.WORK]) for phone in phones],
        addresses=[
            Address(
                country=country,
                localcity=city,
                postal_code=zip_code,
                region=region,
                types=[address_type],
                street=street,
            )
        ],
        organization=Organization(name=organization),
        title=title,
        url=url,
    )
    vcard.to_file(output_path)
    typer.echo(f"VCard generated at {output_path}")


@app.command()
def create_qr_code(
    country: Annotated[str, typer.Option("--country", "-co")] = "",
    city: Annotated[str, typer.Option("--city", "-ci")] = "",
    zip_code: Annotated[str, typer.Option("--zip-code", "-z")] = "",
    region: Annotated[str, typer.Option("--region", "-r")] = "",
    street: Annotated[str, typer.Option("--street", "-s")] = "",
    address_type: AdrType = AdrType.WORK,
    family_name: Annotated[str, typer.Option("--family-name", "-f")] = "",
    given_name: Annotated[str, typer.Option("--given-name", "-g")] = "",
    formatted_name: Annotated[str, typer.Option("--formatted-name", "-fn")] = "",
    additional_names: Annotated[
        list[str], typer.Option("--additional-name", "-a")
    ] = [],
    honorific_prefixes: Annotated[list[str], typer.Option("--prefix", "-p")] = [],
    honorific_suffixes: Annotated[list[str], typer.Option("--suffix", "-s")] = [],
    nickname: Annotated[str, typer.Option("--nickname", "-n")] = "",
    emails: Annotated[list[str], typer.Option("--email", "-e")] = [],
    phones: Annotated[list[str], typer.Option("--phone", "-ph")] = [],
    organization: Annotated[str, typer.Option("--organization", "-org")] = "",
    title: Annotated[str, typer.Option("--title", "-t")] = "",
    urls: Annotated[list[str], typer.Option("--url", "-u")] = [],
    version: Annotated[Version, typer.Option()] = Version.v3,
    photo: Annotated[Path, typer.Option("--photo", "-p")] = None,
    logo: Annotated[Path, typer.Option("--logo", "-l")] = None,
    output_path: Annotated[str, typer.Option("--output", "-o")] = "./qrcode.svg",
):
    vcard_class = VERSION[version]
    name_obj = Name(
        family_name=family_name,
        given_name=given_name,
        additional_names=";".join(additional_names),
        honorific_prefixes=";".join(honorific_prefixes),
        honorific_suffixes=";".join(honorific_suffixes),
    )
    vcard = vcard_class(
        name=name_obj,
        nickname=nickname,
        formatted_name=formatted_name
        if formatted_name
        else f"{given_name} {family_name}"
        if not additional_names
        else f"{given_name} {' '.join(additional_names)} {family_name.upper()}",
        emails=[Email(value=email, types=[EmailType.INTERNET]) for email in emails],
        telephones=[Telephone(value=phone, types=[TelType.WORK]) for phone in phones],
        addresses=[
            Address(
                country=country,
                localcity=city,
                postal_code=zip_code,
                region=region,
                types=[address_type],
                street=street,
            )
        ],
        organization=Organization(name=organization),
        title=title,
        url=urls,
        photo=Photo(data=photo.read_bytes()) if photo else None,
    )
    vcard_string = vcard.to_vcard()

    qr_svg = generate_qr_svg(vcard_string)

    if logo:
        qr_svg = embed_logo_in_svg(qr_svg, logo, logo_scale=0.2)
    with open(output_path, "w+", encoding="utf-8") as f:
        f.write(qr_svg)
    typer.echo(f"QR Code generated at {output_path}")


def main():
    app()


if __name__ == "__main__":
    main()
