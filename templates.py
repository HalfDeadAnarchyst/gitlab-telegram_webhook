import datetime as dt

web_url = "https://lab.rotek.ru/"


def parser_tag_push(data):
    output = f'[tag push] <a href=\"{data["project"]["web_url"]}\">{data["project"]["path_with_namespace"]}</a>: ' \
             f'ver <a href=\"{data["project"]["web_url"]}/commit/{data["after"]}\">{data["ref"].split("/")[2]}</a> ' \
             f'by {data["user_name"]}'
    return output


def parser_issue(data):
    s = ""
    if data["object_attributes"]["action"] == "update":
        s = "d"
    else:
        s = "ed"
    output = f'[issue] <a href=\"{data["project"]["web_url"]}\">{data["project"]["path_with_namespace"]}</a>: ' \
             f'{data["object_attributes"]["action"]}{s} ' \
             f'<a href=\"{data["object_attributes"]["url"]}\">{data["object_attributes"]["title"]}</a> ' \
             f'by <a href=\"{web_url}{data["user"]["username"]}\">{data["user"]["username"]}</a>\n'
    return output


def parser_note(data):
    output = f'[note] <a href=\"{data["project"]["web_url"]}\">{data["project"]["path_with_namespace"]}</a>: ' \
             f'in {data["object_attributes"]["url"]} by' \
             f'<a href=\"{web_url}{data["user"]["username"]}\">{data["user"]["username"]}</a>\n' \
             f'comment: {data["object_attributes"]["note"]}'
    return output


def parser_merge_request(data):
    output = f'[merge request] <a href=\"{data["project"]["web_url"]}\">{data["project"]["path_with_namespace"]}</a>: '\
             f'from <a href=\"{data["repository"]["homepage"]}/tree/{data["source_branch"]}\">' \
             f'{data["object_attributes"]["source_branch"]}</a> ' \
             f'to <a href=\"{data["repository"]["homepage"]}/tree/{data["target_branch"]}\">' \
             f'{data["object_attributes"]["target_branch"]}</a> ' \
             f'is <a href=\"{data["object_attributes"]["url"]}\">{data["object_attributes"]["state"]}</a> ' \
             f'and {data["object_attributes"]["merge_status"]}'
    return output


def parser_pipeline(data):
    output = f'[Pipeline] <a href=\"{data["project"]["web_url"]}\">{data["project"]["name"]}</a>: ' \
             f'\n'
    for stage in data["builds"].reverse():
        output += f'<a href=\"{data["project"]["web_url"]}/-/jobs/{stage["id"]}\">' \
             f'{stage["stage"]}</a> {stage["status"]} '
        if (str(stage["started_at"]) != "None") and (str(stage["finished_at"]) != "None"):
            daytime_start = str(stage["started_at"]).split(" ")
            day_start = daytime_start[0].split("-")
            time_start = daytime_start[1].split(":")
            daytime_end = str(stage["finished_at"]).split(" ")
            day_end = daytime_end[0].split("-")
            time_end = daytime_end[1].split(":")
            start = dt.datetime(int(day_start[0]),  int(day_start[1]),  int(day_start[2]),
                                int(time_start[0]), int(time_start[1]), int(time_start[2]))
            end = dt.datetime(int(day_end[0]),  int(day_end[1]),  int(day_end[2]),
                              int(time_end[0]), int(time_end[1]), int(time_end[2]))
            output += f'in {(end-start).total_seconds()}\n'
            print((end-start).total_seconds())
        else:
            output += "\n"

    return output


def parser_build(data):
    if data['build_status'] in ("running", "created", "canceled"):
        return ''
    # BAD WORKAROUND
    if data["build_stage"] != 'build':
        return ''
    output = f'[build] <a href=\"{data["repository"]["homepage"]}\">{data["project_name"]}</a>: ' \
             f'<a href=\"{data["repository"]["homepage"]}/-/jobs/{data["build_id"]}\">' \
             f'{data["build_stage"]} {data["build_status"]}</a> in {str(data["build_duration"])}'
    return output


def parser_wiki(data):
    output = f'[wiki] <a href=\"{data["project"]["web_url"]}\">{data["project"]["path_with_namespace"]}</a>: ' \
             f'{data["object_attributes"]["action"]}d ' \
             f'<a href=\"{data["object_attributes"]["url"]}\">{data["object_attributes"]["title"]}</a> by ' \
             f'<a href=\"{web_url}{data["user"]["username"]}\">' \
             f'{data["user"]["username"]}</a>\n'

    if data["object_attributes"].get('message', "None") != "None":
        output += f'1. {data["object_attributes"]["message"]}\n'
    return output


def parser_push_gitlab(data):
    branch = data["ref"].split("/")[2]
    s = ""
    if len(data["commits"]) > 1:
        s = "s"
    output = f'[push] <a href=\"{data["project"]["web_url"]}\">{data["project"]["path_with_namespace"]}</a>: ' \
             f'<a href=\"{data["repository"]["homepage"]}/tree/{branch}\">{branch}</a> '
    if data["after"] == "0000000000000000000000000000000000000000":
        output += f'is deleted by <a href=\"{web_url}{data["user_username"]}\">' \
                  f'{data["user_username"]}</a>\n'
    elif data["before"] == "0000000000000000000000000000000000000000":
        output += f'is created by <a href=\"{web_url}{data["user_username"]}\">' \
                  f'{data["user_username"]}</a>\n'
    else:
        output += f'{len(data["commits"])} ' \
                  f'<a href=\"{data["repository"]["homepage"]}/commit/{data["after"]}\">commit{s}</a> ' \
                  f'pushed by <a href=\"{web_url}{data["user_username"]}\">' \
                  f'{data["user_username"]}</a>\n'
    if len(data["commits"]) != 0:
        for element in data["commits"]:
            output += f'{data["commits"].index(element)+1}. {element["message"]}\n'
    return output


def parser_push_gogs(data):
    branch = data["ref"].split("/")[2]
    s = ""
    if len(data["commits"]) > 1:
        s = "s"
    output = f'[push] <a href=\"{data["repository"]["html_url"]}\">{data["repository"]["full_name"]}</a>: ' \
             f'<a href=\"{data["repository"]["html_url"]}/src/{branch}\">{branch}</a> '
    if data["after"] == "0000000000000000000000000000000000000000":
        output += f'is deleted by <a href=\"{web_url}{data["pusher"]["username"]}\">' \
                  f'{data["pusher"]["username"]}</a>\n'
    elif data["before"] == "0000000000000000000000000000000000000000":
        output += f'is created by <a href=\"{web_url}{data["pusher"]["username"]}\">' \
                  f'{data["pusher"]["username"]}</a>\n'
    else:
        output += f'{len(data["commits"])} <a href=\"{data["compare_url"]}\">commit{s}</a> ' \
                  f'by <a href=\"{web_url}{data["pusher"]["username"]}\">' \
                  f'{data["pusher"]["username"]}</a>\n'
    for element in data["commits"]:
        output += f'{data["commits"].index(element)+1}. {element["message"]}\r'
    return output