from utils import hook, HookFlags, JsonResponse
from utils.date import pretty_date
from libs import centarra

@hook.command("ticket list", doc=("List a short summery of every ticket linked to your account.","Usage:","\t`ticket list'"))
  # ticket is the only user-accessible directory in support and "support list" is weird.
def list(args, flags):  # I'd rather not spit every ticket reply out at them at once in this command...
    reply = centarra("/support/tickets")
    rpl = []
    for ticket in reply['tickets']:
        form = {
            "open": "OPEN" if ticket['is_open'] else "CLOSED",
            "o_t": pretty_date(ticket['opened_at']),
            "closed": "\tclosed %s" % pretty_date(ticket['closed_at']) if not ticket['is_open'] else "\t\t"
                }
        rpl.append("#{ticket} by {user}\t{open}\t\tOpened {o_t}{closed}\tSubject: \"{subject}\"".format(**(dict(form.items() + ticket.items()))))
    return JsonResponse(reply, "\r\n".join(rpl))

@hook.command("ticket view", args_amt=1, doc=("View detailed information regarding a specific ticket.", "Usage:", "\t`ticket view <ticket_id>'"))
def view(args, flags):
    reply = centarra("/support/ticket/%s" % args[0])
    ticket = reply['ticket']
    form = {
            "open": "OPEN" if ticket['is_open'] else "CLOSED",
            "o_t": pretty_date(ticket['opened_at']),
            "closed": "\tclosed %s" % pretty_date(ticket['closed_at']) if not ticket['is_open'] else "\t\t"
    }
    rpl = ("#{ticket} by {user}\t{open}\t\tOpened {o_t}{closed}\tSubject: \"{subject}\"\r\n".format(**(dict(form.items() + ticket.items()))))
    for i in ticket['replies']:
        rpl += ("\r\nReply {ago}, by {user}:\r\n" + ("-" * 10) + "\r\n{message}\r\n" + ("-" * 10)).format(ago=pretty_date(i['replied_at']), **i)
    return JsonResponse(reply, rpl)

# TODO it's very clear that I need a clean way to format my stuff into readable output, this has been awful

@hook.command("ticket close", args_amt=1, doc=("Close a currently-open ticket.","Usage:","\t`ticket close <ticket_id>'"))
def close(args, flags):
    reply = centarra("/support/ticket/%s/close" % args[0])
    return JsonResponse(reply, "Ticket %s has been closed." % args[0])

@hook.command("ticket create", args_amt=2, doc=("Create a new ticket with a subject and a message.", "Usage:", "`ticket create <subject> <message>'"))
def create(args, flags):
    reply = centarra("/support/ticket/new", subject=args[0], message=args[1])
    return JsonResponse(reply, "Your ticket, with ID %s, has been created successfully." % reply['ticket']['ticket'])
