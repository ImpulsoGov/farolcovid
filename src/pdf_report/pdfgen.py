import weasyprint
import random
import os
import sys
import tempfile
from datetime import datetime
import subprocess
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import logging

logging.getLogger("googleapicliet.discovery_cache").setLevel(logging.ERROR)
import binascii
import pickle
import plotly.io as pio
import math

pio.orca.config.executable = "/usr/bin/orca"
pio.orca.config.use_xvfb = True
# pio.orca.config.save()
# sys.path.insert(0, "..")
import plots as plots
import model.simulator as simulator
import utils

# example_recife_id = 2611606
separator = "$#"
path_standard = "pdf_report/models"
single_page_path = "pagefull.html"


def convert_path(fpath):
    """
    if we need to afterwards...
    """
    return fpath


def check_necessary_values(model_path=None):
    if model_path != None:
        html_file = open(model_path, "r")
        content = html_file.read()
        html_file.close()
        parts = [a for i, a in enumerate(content.split(separator)) if i % 2 == 1]
        parts = list(set(parts))
        return parts
    else:
        parts = []
        for name in pages_standard:
            path = os.path.join(path_standard, name)
            html_file = open(path, "r")
            content = html_file.read()
            html_file.close()
            parts = parts + [
                a for i, a in enumerate(content.split(separator)) if i % 2 == 1
            ]
            parts = list(set(parts))
        return parts


def gen_simulacovid_results(user_input, config):
    scenarios = ["isolation", "lockdown", "nothing"]
    out_names = [
        ["tempo_colapso_estavel_leitos", "tempo_colapso_estavel_leitos_uti"],
        ["tempo_colapso_positivo_leitos", "tempo_colapso_positivo_leitos_uti"],
        ["tempo_colapso_negativo_leitos", "tempo_colapso_negativo_leitos_uti"],
    ]
    scenarios_results = dict()
    for i, scenario in enumerate(scenarios):
        adapt_user_input = user_input.copy()
        adapt_user_input["strategy"] = scenario
        dfs = simulator.run_simulation(user_input, config)
        dday_beds = simulator.get_dmonth(dfs, "I2", int(user_input["number_beds"]))
        dday_icu_beds = simulator.get_dmonth(
            dfs, "I3", int(user_input["number_icu_beds"])
        )
        scenarios_results[out_names[i][0]] = process_simula_result(dday_beds["best"])
        scenarios_results[out_names[i][1]] = process_simula_result(
            dday_icu_beds["best"]
        )
        if scenario == "isolation":
            simula_plot_file = gen_simulacovid_plot(dfs, user_input)[0]
    scenarios_results["simulacovid_plot_path"] = convert_path(simula_plot_file.name)
    return simula_plot_file, scenarios_results


def process_simula_result(simula_result):
    if simula_result == 1:
        return f"em até {simula_result} mês"
    elif simula_result == 2:
        return f"em até {simula_result} meses"
    else:
        return f"+ de 2 meses"


def gen_simulacovid_plot(dfs, user_input):
    figure = plots.plot_simulation(dfs, user_input)
    figure.update_layout(autosize=False, width=1701, height=800)
    figure_bytes = figure.to_image(format="png")
    fig_temp_file = tempfile.NamedTemporaryFile()
    fig_temp_file.write(figure_bytes)
    return [fig_temp_file]


def _gen_place_plots(place_id):
    """
    Generate plots to the PDF file
    """
    place_type = ["state_num_id", "health_region_id", "city_id"][
        math.floor(math.log10(min(10 ** 3, place_id))) - 1
    ]
    plots_dict = {
        "social_distancing": {"plot": plots.gen_social_dist_plots(place_id)},
        "rt": {"plot": plots.plot_rt_wrapper(place_id, place_type)},
        "file_objects": list(),
    }

    for k in plots_dict.keys():
        if k != "file_objects":
            # Generate temp file
            plots_dict[k]["temp_file"] = tempfile.NamedTemporaryFile()
            # Write content
            plots_dict[k]["temp_file"].write(
                plots_dict[k]["plot"]
                .update_layout(autosize=False, width=1701, height=450)
                .to_image(format="png")
            )
            # Define paths
            plots_dict["file_objects"].append(plots_dict[k]["temp_file"])
            plots_dict[k]["path"] = convert_path(plots_dict[k]["temp_file"].name)

    return plots_dict


def sub_html(model_path, args_dict):
    with open(model_path, "r") as html_file:
        content = html_file.read()

    for target in check_necessary_values(model_path):
        content = content.replace(
            separator + str(target) + separator, str(args_dict[target])
        )

    return content


def render_html_pagefull(model_path, args_dict):
    css_files = []
    css_file_names = [i for i in os.listdir(path_standard) if ".css" in i]

    for file_name in css_file_names:
        css_file = open(os.path.join(path_standard, file_name), "r")
        css_data = css_file.read()
        css_file.close()
        css = weasyprint.CSS(string=css_data)
        css_files.append(css)

    return weasyprint.HTML(string=sub_html(model_path, args_dict), base_url="/").render(
        stylesheets=css_files, enable_hinting=False
    )


def compress_pdf_file(input_file_path, output_file_path, power=0, showresults=False):
    # Stolen from theeko74
    """Function to compress PDF via Ghostscript command line interface"""
    quality = {0: "/default", 1: "/prepress", 2: "/printer", 3: "/ebook", 4: "/screen"}
    # Basic controls
    # Check if valid path
    if not os.path.isfile(input_file_path):
        print("Error: invalid path for input PDF file")
        sys.exit(1)

    # Check if file is a PDF by extension
    # if input_file_path.split(".")[-1].lower() != "pdf":
    # print("Error: input file is not a PDF")
    # sys.exit(1)

    initial_size = os.path.getsize(input_file_path)
    subprocess.call(
        [
            "gs",
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            "-dPDFSETTINGS={}".format(quality[power]),
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            "-sOutputFile={}".format(output_file_path),
            input_file_path,
        ]
    )
    final_size = os.path.getsize(output_file_path)
    ratio = 1 - (final_size / initial_size)
    if showresults:
        print("Compression by {0:.0%}.".format(ratio))
        print("Final file size is {0:.1f}MB".format(final_size / 1000000))


def upload_file_gdrive(filepath):

    drive_service = build(
        "drive",
        "v3",
        credentials=pickle.loads(binascii.unhexlify(os.getenv("GOOGLE_TOKEN"))),
        cache_discovery=False,
    )

    file_id = (
        drive_service.files()
        .create(
            body={
                "name": str(utils.gen_hash_code(size=16)) + ".pdf",
                "parents": [os.getenv("PDF_FOLDER_ID")],
            },
            media_body=MediaFileUpload(
                filepath, mimetype="application/pdf", resumable=True
            ),
            fields="id",
        )
        .execute()
    ).get("id")

    subprocess.call(["rm", filepath])

    return file_id


def generate_download_button(file_id):
    file_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    return f'<div class="base-wrapper"><a href="{file_url}" download="relatorio.pdf" class="btn-ambassador">Clique aqui para baixar</a></div>'


def gen_dict_from_card(card):
    """
    Recover indicators values from cards displays texts.
    """
    # TODO: we need to add a data value on Indicators class to make it easy. Some extra work to do this...

    add_dict = dict()
    if card.header == "Ritmo de Contágio":
        add_dict["numero_contagio_low"] = card.display.split(" a ")[0]
        add_dict["numero_contagio_high"] = card.display.split(" a ")[1]
        add_dict["numero_contagio_sempass_low"] = card.left_display.split(" a ")[0]
        add_dict["numero_contagio_sempass_high"] = card.left_display.split(" a ")[1]
        add_dict["tendencia_contagio"] = card.right_display + " 📈"
        add_dict.update(
            convert_risk(
                card.risk,
                ["is_spread_bad", "is_spread_unsatisfactory", "is_spread_good"],
            )
        )
    elif card.header == "Subnotificação":
        add_dict["contagem_subnot"] = card.display
        add_dict["ranking_subnot_uf"] = card.right_display
        add_dict.update(
            convert_risk(
                card.risk, ["is_sub_bad", "is_sub_unsatisfactory", "is_sub_good"]
            )
        )
    elif card.header == "Capacidade Hospitalar*":
        add_dict["numero_capacidade_hospitalar"] = card.display
        add_dict.update(
            convert_risk(
                card.risk,
                ["is_hospital_bad", "is_hospital_unsatisfactory", "is_hospital_good"],
            )
        )
    elif card.header == "Isolamento Social":
        add_dict["taxa_isolamento"] = card.display
        add_dict["taxa_isolamento_sempass"] = card.left_display
        add_dict["tendencia_isolamento"] = card.right_display
    else:
        # print(card.header)
        raise ValueError("The card could not be identified")

    return add_dict


def convert_risk(risk, options):
    """
    Activate elements related to specific risk level (ex: farol, labels)
    """

    values = ["hidden", "hidden", "hidden"]
    diferential_dict = dict()
    if risk == "ruim" or risk == "alto":
        values[0] = "normal"
    elif risk == "insatisfatório" or risk == "médio":
        values[1] = "normal"
    elif risk == "bom" or risk == "baixo":
        values[2] = "normal"
    else:
        raise ValueError("Risk not identified")
    for i, option in enumerate(options):
        diferential_dict[option] = values[i]

    return diferential_dict


def gen_basic_data(user_input):
    return {
        "data": datetime.today().strftime("%d/%m/%Y"),
        "nome_lugar": user_input["locality"],
        "leitos": user_input["number_beds"],
        "leitos_uti": user_input["number_icu_beds"],
        "casos_ativos": user_input["population_params"]["I"],
        "mortes": user_input["population_params"]["D"],
        "casos_confirmados": user_input["population_params"]["I_confirmed"],
    }


def parse_user_input(user_input, indicators, data, config, test=False):
    """
    Parse all content to a dict for PDF
    """
    risco_geral = data["overall_alert"].values[0]

    # Start inputs for PDF
    content_dict = gen_basic_data(user_input)

    # Recover indicators values from cards values
    for in_card in indicators.values():
        content_dict.update(gen_dict_from_card(in_card))

    # Risco
    content_dict.update(
        convert_risk(risco_geral, ["is_high_risk", "is_medium_risk", "is_low_risk"])
    )

    # TODO: CHECK THIS NEW CALL TO IDS!
    # Place plots
    if user_input["city_name"] == "Todos":
        plots_dict = _gen_place_plots(user_input["state_num_id"])
    else:
        plots_dict = _gen_place_plots(user_input["city_id"])

    # plots_dict = _gen_place_plots(
    #     utils.get_place_id_by_names(user_input["state_name"], user_input["city_name"])
    # )

    content_dict["isolamento_plot_path"] = plots_dict["social_distancing"]["path"]
    content_dict["contagio_plot_path"] = plots_dict["rt"]["path"]

    # Simulacovid results
    simulacovid_resultfile, simulacovid_data = gen_simulacovid_results(
        user_input, config
    )
    plots_dict["file_objects"].append(simulacovid_resultfile)
    temp_files = plots_dict["file_objects"]
    content_dict.update(simulacovid_data)

    # TEST: To check the inputs used for plots - use it alone
    if test:
        for temp_file in temp_files:
            temp_file.close()
        return content_dict

    # Ouputs to generate the PDF
    else:
        return (content_dict, temp_files)


def gen_pdf_report(user_input, indicators, data, config, compress=True):
    """
    Entrypoint to construct the PDF file from user request.
    """

    substitutions, temp_files = parse_user_input(user_input, indicators, data, config)

    pdf_file_bytes = render_html_pagefull(
        os.path.join(path_standard, single_page_path), substitutions
    ).write_pdf()
    pdf_file = tempfile.NamedTemporaryFile()
    pdf_file.write(pdf_file_bytes)

    [file_object.close() for file_object in temp_files]

    if compress:
        out_filepath = pdf_file.name + "compressed.pdf"
        compress_pdf_file(pdf_file.name, out_filepath, 2)
        pdf_file.close()
    else:
        out_filepath = pdf_file.name

    return generate_download_button(upload_file_gdrive(out_filepath))


if __name__ == "__main__":
    pass
