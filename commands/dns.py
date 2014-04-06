from utils import hook, HookFlags, JsonResponse
from utils.domain import is_valid_host
from libs import centarra, sub

flags = HookFlags(l="long")


@hook.command('dns zones', flags=flags)
def zones(args, flags):
    reply = centarra('/dns/zones')
    resp = []
    for zone in reply['zones']:
        a = "Zone #{id} - {name}, owned by {user}, with {x} records assigned.".format(x=len(zone['records']), **zone)
        if 'l' in flags:
            a += "\r\n\tID\t\tType\t\tPriority\tTTL\t\tContent"
            for record in zone['records']:
                a += "\r\n\t({id}):\t\t{type}\t\t{prio}\t\t{ttl}\t\t\"{content}\"".format(**record)
        resp.append(a)
    return JsonResponse(reply, "\r\n".join(resp))


flags = HookFlags(p="priority", t="ttl")


@hook.command('dns zone', args_amt=1, flags=flags)
def zone(args, flags):
    reply = centarra('/dns/zone/%s' % args[0])
    zone = reply['zone']
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


@hook.command('dns create', args_amt=1)
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


@hook.command("dns edit-record", args_amt=4)
def edit_record(args, flags):
    reply = centarra("/zone/%s/record/%s" % (args[0], args[1]), subdomain=args[2], content=args[3])
    return JsonResponse(reply, "Record {id} was successfully updated - {sub}{dot}{name} set to {content}"
    .format(**reply['zone'], dot="." if args[2] is not "" else "", sub=args[2], content=args[3], id=args[1]))


flags = HookFlags(t=("ttl", True), p=("priority", True))
@hook.command("dns add-record", args_amt=lambda x: len(x) == 2 if x[0] == "valid" else len(x) == 4, flags=flags)
def add_record(args, flags):
    if args[1] == "valid":
        reply = centarra('/zone/%s/record/new' % args[0])
        return JsonResponse(reply, "Available records:" + ', '.join(reply['record_types']))
    else:  # id subdomain type content
        send = {"subdomain": args[1], "type": args[2], "content": args[3], 'ttl': flags.get('t', 300),
                "prio": flags.get('p', 0)}
        reply = centarra("/zone/%s/record/new" % args[0], **send)
        return JsonResponse(reply, "{subdomain}{dot}{domain} was set as {type} to {content}."
                                   + ("\tTTL = {ttl}" if 't' in flags else "")
                                   + ("\tPriority = {prio}" if 'p' in flags else "").format(
                        dot="." if send['subdomain'] is not "" else "",
                        domain=reply['zone']['name'],
                        **send)
        )

@hook.command("dns delete-record", args_amt=2)
def delete_record(args, flags):
    reply = centarra("/zone/%s/record/%s/delete" % (args[0], args[1]))
    return JsonResponse(reply, "Your record %s in domain %s has been deleted." % (args[1], args[0]))


@hook.command("dns delete", args_amt=1)
def delete(args, flags):
    reply = centarra("/zone/%s/delete" % args[0])
    return JsonResponse(reply, "Your zone %s has been successfully deleted." % args[0])

@hook.command("dns axfr-import")
def axfr_import(args, flags):
    reply = centarra("/zone/%s/axfr-import" % args[0], nameserver=args[1])
    return JsonResponse(reply, "Your axfr-import process is running for domain %s on nameserver %s" % (args[0], args[1]))
