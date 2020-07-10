import sys

try:
    css_in = sys.argv[1]
    html_in = sys.argv[2]
except:
    print("Please pass the raw css filepath first and then the html filepath")
css_file = open(css_in, "r")
html_file = open(html_in, "r")
css = css_file.readlines()
css = [i.replace("\n", "") for i in css]
css = [i for i in css if "/* or " not in i]
css = [i for i in css if "/* identical to box height */" not in i]
html = html_file.readlines()
css_file.close()
html_file.close()
css_headers = [
    i.replace("/* ", "").replace(" */", "").replace("\n", "") for i in css if "/*" in i
]
css_headers_raw = [i for i in css if "/*" in i]
# print("*/")
# print(css_splits)
classes = []


def get_html_headers(html):
    for i, line in enumerate(html):
        if "<!--" in line:
            header = line.replace("\n", "").replace("<!-- ", "").replace(" -->", "")
            # cleaning identing
            header = "".join(
                [
                    a
                    for i, a in enumerate(header)
                    if header[: i + 1].count(" ") < len(header[: i + 1])
                ]
            )
            data = html[i + 1].replace("\n", "")
            count = i + 2
            while (
                "div" not in html[count]
                and "/div" not in html[count]
                and "<!" not in html[count]
                and "<span" not in html[count]
                and "</body>" not in html[count]
            ):
                data = data + html[count].replace("\n", "")
                count += 1
            splitted = data.split('"')
            identification = splitted[splitted.index(" id=") + 1]
            classes.append([header, identification])
    return classes


def find_html_id(html, header):
    header_pairs = get_html_headers(html)
    names = [i[0] for i in header_pairs]
    pos = names.index(header)
    return header_pairs[pos][1]


new_css = list(css)
shift = 0
for index, css_line in enumerate(css):
    if "/*" in css_line:
        header = css_line.replace("/* ", "").replace(" */", "")
        html_id = find_html_id(html, header)
        add1 = "#" + html_id + "{"
        add2 = "}"
        end_index = index + 1
        while end_index < len(css) and "/*" not in css[end_index]:
            end_index += 1
        end_index = end_index - 1
        shift += 2
        new_css.insert(index + shift, add1)
        new_css.insert(end_index + shift, add2)
        # print(header, html_id, " - ", index, end_index)
clean_css = "\n".join(new_css)
css_out_name = ".".join(html_in.split(".")[:-1]) + ".css"
css_out = open(css_out_name, "w")
css_out.write(clean_css)
css_out.close()
