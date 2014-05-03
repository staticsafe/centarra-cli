from utils import hook, HookFlags, JsonResponse
from libs import centarra
from utils.date import pretty_date
import math

flags = HookFlags(l="long")

@hook.command("invoice list", flags=flags, doc=("View a list of all invoices attached to your account",
                                                "Flags:",
                                                "\t-l, --long: Display more detailed information about each invoice.",
                                                "Usage:",
                                                "\t`invoice list'"))
def list(args, flags):
    reply = centarra("/invoice/list")
    resp = []
    for i in reply['invoices']:
        a = ("{invoice}\t\tBy {user}\t\tBalance ${total:.2f}\t\tCreated {cr}"
            + (", paid {pa}." if i['payment_ts'] is not None else ".")).format(
                cr=pretty_date(i['creation_ts']),
                pa=pretty_date(i['payment_ts']),
                **i)
        if 'l' in flags:
            for j in i['items']:
                a += "\r\n\t{line_item}\t${price:.2f}\t\t{ts}\t\"{description}\"".format(
                    ts=pretty_date(j['entry_ts']),
                    **j)
            a += "\r\n" + "-" * 30
        resp.append(a)
    return JsonResponse(reply, "\r\n".join(resp))

@hook.command("invoice view", args_amt=1, doc=("View detailed information regarding a single invoice.",
                                               "Usage:",
                                               "\t`invoice view <invoice_id>'"))
def view(args, flags):
    reply = centarra("/invoice/%s" % args[0])
    i = reply['invoice']
    a = ("{invoice}\t\tBy {user}\t\tBalance {total:.2f}\t\tCreated {cr}"
            + (", paid {pa}." if i['payment_ts'] is not None else ".")).format(
                cr=pretty_date(i['creation_ts']),
                pa=pretty_date(i['payment_ts']),
                **i)
    for j in i['items']:
        a += "\r\n\t{line_item}\t${price:.2f}\t\t{ts}\t\"{description}\"".format(
            ts=pretty_date(j['entry_ts']),
            **j)
    return JsonResponse(reply, a)


@hook.command("invoice credit", args_amt=lambda x: not x or len(x) == (2 if x[0] == "add" else 0),
              doc=("View or edit the amount of service credit you have in your account.",
                   "All arguments can be omitted if you intend to view your credit.",
                   "The argument when adding credit must be above $1.00, and formatted like a float.",
                   "Usage:",
                   "\t`invoice credit'"
                   "\t`invoice credit add <amount>'"))
def credit(args, flags):
    if args and args[0] == "add":
        reply = centarra("/invoice/svccredit", creditamt=args[1])
        if "invoices" in reply:
            return JsonResponse(reply, "Adding service credit failed. Make sure your value was formatted correctly and is over $1.00.")
        return JsonResponse(reply, "Invoice {invoice} was created for a value of {total}. See `invoice view {invoice}' for more information.".format(**(reply['invoice'])))
    else:
        reply = centarra("/invoice/service_credit.json")
        return JsonResponse(reply, "User {username} has ${total:.2f} in total service credit.".format(**reply))

@hook.command("invoice resend", args_amt=1, doc=("Resend an e-mail to yourself regarding an invoice.",
                                                 "Usage:",
                                                 "\t`invoice resend <invoice_id>'"))
def resend(args, flags):
    reply = centarra("/invoice/%s/resend" % args[0])
    return JsonResponse(reply, "Your invoice has been successfully resent.")

@hook.command("invoice apply-credit", args_amt=1, doc=("Apply account service credit to this invoice.",
                                                       "If the service credit amount is not enough, all available credit will be applied.",
                                                       "Usage:",
                                                       "\t`invoice apply-credit <invoice_id>'"))
def apply_credit(args, flags):
    reply = centarra("/invoice/%s/svccredit" % args[0])
    return JsonResponse(reply, "Service credit has been applied to invoice %s." % args[0])
