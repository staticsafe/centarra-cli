from utils import hook, HookFlags, JsonResponse
from libs import centarra
from utils.date import pretty_date

@hook.command("incident list", doc=("View a list of all incidents recorded in the panel.", "Usage:", "\t`incident list'"))
def get(args, flags):
    reply = centarra("/status/incidents")
    rpl = []
    for i in reply['incidents']:
        rpl.append("#{incident} (by {user} {time}) - ({open}) \"{subject}\"".format(open="OPEN" if i['is_open'] else "CLOSED",
                                                                                      time=pretty_date(i['opened_at']),
                                                                                      **i))
    rpl.reverse()
    return JsonResponse(reply, "\r\n".join(rpl))

@hook.command("incident view", args_amt=1, doc=("View specific information on a incident recorded in the panel.",
                                                "Usage:",
                                                "\t`incident view <incident_id>'"))
def view(args, flags):
    reply = centarra("/status/incident/%s" % args[0])
    incident = reply['incident']
    rpl = []
    rpl.append("#{incident} (by {user} {time}) - ({open}) \"{subject}\"".format(open="OPEN" if incident['is_open'] else "CLOSED",
                                                                                      time=pretty_date(incident['opened_at']),
                                                                                      **incident))
    for i in incident['replies']:
        rpl.append("\t{user} {time}: {message}".format(time=pretty_date(i['replied_at']), **i))
    return JsonResponse(reply, "\r\n".join(rpl))
