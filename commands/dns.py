from utils import hook, HookFlags, JsonResponse
from utils.domain import is_valid_host
from libs import centarra, substitutes
import time

flags = HookFlags(l="long")


def needs_update(category):
    if substitutes.data.get(category, False):
        current = substitutes.data[category]
        for i in current:
            if current[i]['expiry'] < time.time():
                return True
    else:
        return True
    return False

def update_dns_zones():
    if not needs_update('dns zones'):
        return
    substitutes.data['vps list'] = {}
    reply = centarra('/dns/zones')
    for zone in reply['zones']:
        substitutes.sub('dns zones', zone['name'], zone['id'])


@hook.command('dns zones', flags=flags, doc=("View all domain zones associated with your account.",
                                             "This will display a short summary of all domains that are listed in your account.",
                                             "All domains will be aliased to their IDs as variables if they are not already set.",
                                             "Flags:",
                                             "\t-l, --long: Display detailed information regarding each zone",
                                             "Usage:",
                                             "\t`dns zones [-l]'"))
def zones(args, flags):
    reply = centarra('/dns/zones')
    resp = []
    for zone in reply['zones']:
        substitutes.sub('dns zones', zone['name'], zone['id'])
        a = "Zone #{id} - {name}, owned by {user}, with {x} records assigned.".format(x=len(zone['records']), **zone)
        if 'l' in flags:
            a += "\r\n\tID\t\tType\t\tPriority\tTTL\t\tContent"
            for record in zone['records']:
                a += "\r\n\t({id}):\t\t{type}\t\t{prio}\t\t{ttl}\t\t\"{content}\"".format(**record)
        resp.append(a)
    return JsonResponse(reply, "\r\n".join(resp))


flags = HookFlags(p="priority", t="ttl")

@hook.command('dns zone', args_amt=1, flags=flags, doc=("Display detailed information about a specific DNS zone.",
                                                        "This will display all available information about the dns zone specified.",
                                                        "No records will be aliased to their IDs because of the lack of a unique key to use.",
                                                        "Flags:",
                                                        "\t-p, --priority: Display the priority of each DNS record in this zone",
                                                        "\t-t, --ttl: Display the time-to-live (TTL) of each DNS record in this zone",
                                                        "Usage:",
                                                        "\t`dns zone <zone> [-tp]'"))
def zone(args, flags):
    reply = centarra('/dns/zone/%s' % substitutes.swap("dns zones", args[0]))
    zone = reply['zone']
    substitutes.sub('dns zones', zone['name'], zone['id'])
    a = "Zone #{id} - {name}, owned by {user}, with {x} records assigned".format(x=len(zone['records']), **zone)
    a += "\r\n\tID\t\tType\t\t" \
         + ("Priority\t" if 'p' in flags else "") \
         + ("TTL\t\t" if 't' in flags else "") \
         + "Content"
    for record in zone['records']:
        a += ("\r\n\t({id}):\t\t{type}\t\t"
              + ("{prio}\t\t" if 'p' in flags else "")
              + ("{ttl}\t\t" if 't' in flags else "")
              + "\"{content}\"").format(**record)
    return JsonResponse(reply, a)


@hook.command('dns create', args_amt=1, doc=("Create a new DNS zone in your account.",
                                             "This will create a brand new DNS zone when provided with a hostname.",
                                             "Usage:",
                                             "\t`dns create <hostname>'"))
def new(args, flags):
    reply = centarra('/dns/zone/new', domain_name=args[0])
    if reply == {}:
        # Centarra doesn't provide us with the error, so we have to figure it out ourselves...
        if not is_valid_host(args[0]):
            response = "Domain %s is invalid - Domain zone was not created." % args[0]
        else:
            response = "Domain %s already exists in Centarra's system - Domain zone not created." % args[0]
    else:
        response = "Domain {id} was created. See `dns zone {id}' for more information.".format(**reply['zone'])
    return JsonResponse(reply, response)


@hook.command("dns edit-record", args_amt=4, doc=("Edit a specific record in a DNS zone.",
                                                  "This will allow you to change the subdomain and content of a specific record on your DNS zone.",
                                                  "The subdomain may be empty, or * - but it does not include the complete domain name."
                                                  "Usage:",
                                                  "\t`dns edit-record <zone> <record_id> <subdomain> <content>'"))
def edit_record(args, flags):
    reply = centarra("/zone/%s/record/%s" % (substitutes.swap("dns zones", args[0]), args[1]), subdomain=args[2], content=args[3])
    return JsonResponse(reply, "Record {id} was successfully updated - {sub}{dot}{name} set to {content}"
    .format(dot="." if args[2] is not "" else "", sub=args[2], content=args[3], id=args[1], **(reply['zone'])))


flags = HookFlags(t={"long": "ttl", "param": True}, p={"long": "priority", "param": True})
@hook.command("dns add-record", args_amt=lambda x: len(x) == 2 if x and x[1] == "valid" else len(x) == 4,
              flags=flags, doc=("Add a new record to a DNS zone, or view available records.",
                                "Using the 'valid' argument, you can view a list of available records to add to your subdomain.",
                                "Usage:",
                                "\t`dns add-record <zone_id> valid'\r\n",
                                "Otherwise, you will be allowed to add a new record to your dns zone.",
                                "Flags:",
                                "\t-t, --ttl: Set the time-to-live (TTL) for the new record to be added. Default is 300.",
                                "\t-p, --priority: Set the priority of this record to be added. Default is 0.",
                                "Usage:"
                                "\t`dns add-record <zone> <subdomain> <type> <content> [-t <ttl>][-p <priority>]'"))
def add_record(args, flags):
    if args[1] == "valid":
        reply = centarra('/zone/%s/record/new' % substitutes.swap("dns zones", args[0]))
        return JsonResponse(reply, "Available records:" + ', '.join(reply['record_types']))
    else:  # id subdomain type content
        send = {"subdomain": args[1], "type": args[2], "content": args[3], 'ttl': flags.get('t', 300),
                "prio": flags.get('p', 0)}
        reply = centarra("/zone/%s/record/new" % substitutes.swap("dns zones", args[0]), **send)
        return JsonResponse(reply, "{subdomain}{dot}{domain} was set as {type} to {content}."
                                   + ("\tTTL = {ttl}" if 't' in flags else "")
                                   + ("\tPriority = {prio}" if 'p' in flags else "").format(
                        dot="." if send['subdomain'] is not "" else "",
                        domain=reply['zone']['name'],
                        **send)
        )

@hook.command("dns delete-record", args_amt=2, doc=("Delete a record from your DNS zone.",
                                                    "The record specified will be removed completely from your zone.",
                                                    "Usage:",
                                                    "\t`dns delete-record <zone> <record_id>'"))
def delete_record(args, flags):
    reply = centarra("/zone/%s/record/%s/delete" % (substitutes.swap("dns zones", args[0]), args[1]))
    return JsonResponse(reply, "Your record %s in domain %s has been deleted." % (args[1], substitutes.swap("dns zones", args[0])))


@hook.command("dns delete", args_amt=1, doc=("Delete an entire DNS zone from your account.",
                                             "Warning: this action can not be undone, and should be performed with caution.",
                                             "All records attached to this zone will vanish, along with the zone itself.",
                                             "Usage:",
                                             "\t`dns delete <zone>'"))
def delete(args, flags):
    reply = centarra("/zone/%s/delete" % substitutes.swap("dns zones", args[0]))
    return JsonResponse(reply, "Your zone %s (#%s) has been successfully deleted." % (args[0], substitutes.swap("dns zones", args[0])))

@hook.command("dns axfr-import", args_amt=2, doc=("Import DNS records via axfr.",
                                                  "This will accept a axfr nameserver and import all DNS records via axfr.",
                                                  "Usage:",
                                                  "\t`dns axfr-import <zone> <nameserver>'"))
def axfr_import(args, flags):
    reply = centarra("/zone/%s/axfr-import" % substitutes.swap("dns zones", args[0]), nameserver=args[1])
    return JsonResponse(reply, "Your axfr-import process is running for domain %s on nameserver %s" % (args[0], args[1]))
