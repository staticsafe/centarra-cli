from utils import hook, HookFlags, JsonResponse
from libs import centarra, substitutes, sub
from utils.domain import is_valid_host

flags = HookFlags(l='ip-limits', s='sla', i='ips', m='mac', u='user', w='watchdog', M='memory', S='swap', D='disk')

@hook.command('vps list', flags=flags, doc=("View information on all your current vServers.",
                                                              "Alone, this command returns only a brief list of all your servers.",
                                                              "Using flags, you can display any information you might want about your server:",
                                                              "\t-l, --ip-limits: Display ipv4 and ipv6 IP address limits",
                                                              "\t-s, --sla: Display your server's CPU SLA status",
                                                              "\t-i, --ips: Display a brief list of all your server's ip addresses",
                                                              "\t-m, --mac: Display the MAC address of your server",
                                                              "\t-u, --user: Display the owner of this VPS (probably you)",
                                                              "\t-w, --watchdog: Display if Watchdog monitoring is enabled on this server",
                                                              "\t-M, --memory: Display the amount of memory this server has allocated",
                                                              "\t-S, --swap: Display the amount of SWAP this server has allocated",
                                                              "\t-D, --disk: Display the disk space this server can access.",
                                                              "Running this command will also set up VPS name substitutes if they are not already set.",
                                                              "Usage:",
                                                              "\tvps list [-lsimuwMSD]"))
def list(args, flags):
    reply = centarra('/vps/list')
    for i in reply['vpslist']:
        sub(i['name'], i['id'])
        sub(i['nickname'], i['id'])
    rpl = []
    for i in reply['vpslist']:
        st = '\t{id}: {name} ("{nickname}") on {node}\t\t' + \
             ("IPv6 limit {ipv6_limit}, IPv4 limit {ipv4_limit}\t" if 'l' in flags else '') + \
             ("{cpu_sla} CPU SLA\t" if 's' in flags else '') + \
             ((("IPs: " + ", ".join([j['ip'] for j in i['ips']])) + "\t") if 'i' in flags else '') + \
             ("MAC address {mac}\t" if 'm' in flags else '') + \
             ("Owned by {user}\t" if 'u' in flags else '') + \
             ("Monitoring {monitoring} enabled\t".format(monitoring="is" if i['monitoring'] else "is not") if 'w' in flags else '') + \
             ("{memory}mb memory\t" if 'M' in flags else '') + \
             ("{swap}mb swap\t" if 'S' in flags else '') + \
             ("{disk}gb disk\t" if "D" in flags else '')
        rpl.append(st.format(**i))

    rpl = '\r\n'.join(rpl)
    return JsonResponse(reply, "Your current vServers: \r\n%s" % rpl)

flags = HookFlags(l='ip-limits', b='btc-price', S='swap', M='memory', D='disk')

@hook.command("vps available", args_amt=lambda x: len(x) <= 1, flags=flags, doc=("View available vServers that are currently being sold, as well as available regions.",
                                                "All of the available plans are available here - however, see `vps stock' for information on region stock.",
                                                "This command also sets all resource plan names and region names to variables representing their ids,",
                                                "Therefore using `$Dallas' in a command will have the value of its region id (if it is not already set). Keep in mind you can quote an argument to retain spaces.",
                                                "There are two subcommands available:",
                                                "\tregions: Display regions Centarra supports.",
                                                "\tplans: Display information on plans available for purchase in these regions. This includes plan ID, name, and price (in USD) by default",
                                                "Flags (`plans' subcommand only):",
                                                "\t-l, --ip-limits: Display IPv4 and IPv6 limits on a certain plan",
                                                "\t-b, --btc-price: Display the price of a plan in BTC",
                                                "\t-S, --swap: Display the amount of swap that would be allocated to this plan",
                                                "\t-M, --memory: Display the amount of memory this plan would be allocated (also included in plan names)",
                                                "\t-D, --disk: Display the disk space allocated to this plan",
                                                "Usage:",
                                                "\t`vps available (regions|plans [-lbSMD])'"))
def available(args, flags):
    reply = centarra('/vps/signup')
    for i in reply['regions']:
        sub(i['name'], i['id'])
    for i in reply['resource_plans']:
        sub(i['name'], i['id'])
    rpl = []
    if not args or args[0] == "regions":
        rpl.append("Available Regions: \r\n")
        rpl += ["(%s): %s" % (i['id'], i['name']) for i in reply['regions']]
    if not args or args[0] == "plans":
        rpl.append("Available Plans: \r\n")
        for i in reply['resource_plans']:
            rpl.append(("({id}) '{name}' - ${price_usd}" + (" ({price_btc} BTC)" if 'b' in flags else "") + "."
                       + ("\tIPv4 limit {ipv4_limit}, IPv6 limit {ipv6_limit}" if "l" in flags else "")
                       + ("\tSwap {swap}mb" if 'S' in flags else "")
                       + ("\tMemory {memory}mb" if 'M' in flags else "")
                       + ("\tDisk {disk}gb" if 'D' in flags else "")
            ).format(**i))
    return JsonResponse(reply, '\r\n'.join(rpl))



@hook.command("vps signup", args_amt=2, doc=("Sign up for a brand new VPS using information from `vps available'.",
                                             "This command accepts only a plan and a region - the rest is worked out by deploying.",
                                             "Remember that, after viewing available plans and regions, you can use plan names as variables for their plan ids."
                                             "Usage:",
                                             "\t`vps signup <region> <plan>'",
                                             "Examples:"
                                             "\t`vps signup dallas 512' (after viewing available plans)"))
def signup(args, flags):
    region = args[0].title()

    reply = centarra('/vps/signup', plan=args[1], region=args[0])
    if not reply:
        return JsonResponse(reply, "The selected region did not have enough stock left to satisfy your request. Try using region '0' for a random location.")
    if not reply.get('service', False):
        return JsonResponse(reply, "Your new VPS has been created; please pay invoice {invoice} (${total}) to continue.".format(**reply['invoice']))
    sub(reply['service']['name'], reply['service']['id'], False)
    return JsonResponse(reply, "Your new vps is now named {name} (#{id}) on node {node}. Deploy it with `vps deploy'!"
                                                .format(**reply['service']))


flags = HookFlags(i="ips")
@hook.command("vps info", args_amt=1, flags=flags, doc=("View detailed information regarding your vServer.",
                                            "Flags:"
                                            "\t-i, --ips: Display information on this server's IP addresses",
                                            "Usage:",
                                            "\tvps info <server_id> [-i]",
                                            "Examples:",
                                            "\tvps info $nickname -i"))
def info(args, flags):
    reply = centarra('/vps/%s' % args[0])
    service = reply['service']
    service['w'] = ' not' if not service['monitoring'] else ''
    rpl = "\r\nServer {id} - {name} (\"{nickname}\")" + \
        "\r\n\t{name} is on node {node} with {cpu_sla} CPU SLA status." + \
        "\r\n\t{name} has {memory}mb memory, {swap}mb swap, and {disk}gb disk space." + \
        "\r\n\t{name} is{w} being monitored, and has MAC address {mac}" + \
        "\r\n\t{name} is allowed {ipv6_limit} IPv6 addresses and {ipv4_limit} IPv4 addresses." + \
          (''.join(["\r\n\tIt has IPv{x} address {ip} (id {id})".format(x=i['ipnet']['version'], **i) for i in service['ips']]) if 'i' in flags else '')
    return JsonResponse(reply, rpl.format(**service))


@hook.command("vps templates", args_amt=1, doc=("Display all vps templates available for deployment.",
                                                "This will display all of the names of the xml files available that you can send to the `vps deploy' command.",
                                                "The short names of the deployment templates will also be set as variables pointing to their template names, if the name is not already taken.",
                                                "Usage:",
                                                "\tvps templates <vps_id>"))
def templates(args, flags):
    reply = centarra('/vps/%s/deploy' % args[0])
    for i in reply['templates']:
        sub(reply['templates'][i]['name'], i)
    return JsonResponse(reply, "Templates:\r\n" + '\r\n'.join(["\t%s = %s" % (i, reply['templates'][i]['name']) for i in reply['templates']]))

intent = ['64bit-pvm', '32bit-pvm', 'hvm', 'rescue']  # current intents allowed to be sent

flags = HookFlags(v=('virtualization', True), s='start')
@hook.command("vps deploy", flags=flags, doc=("Deploy your vps with an image so you can start it up.",
                                 "\tWARNING: This process is destructive, and if you deploy an existing vServer, you may lose all data.",
                                 "\tCentarra staff members are not responsible for this data, so be careful.",
                                 "Flags:",
                                 "\t-v, --virtualization <64bit-pvm|32bit-pvm|hvm|rescue>: Change the virtualization type of your vServer. Default is 64bit-pvm",
                                 "\t-s, --start: Start your vps immediately after finishing deployment",
                                 "Usage:",
                                 "\tvps deploy <vps_id> <image_name> <root_password> [-v virtualization] [-s]"))
def deploy(args, flags):
    send = {}
    if 's' in flags:
        send['startvps'] = "on"
    if 'v' in flags:
        if flags['v'] in intent:
            send['intent'] = flags['v']
        else:
            print("Warning: virtualization type is unknown - ignoring value %s" % flags['v'])
    reply = centarra('/vps/%s/deploy' % args[0], imagename=args[1], rootpass=args[2], **send)

    return JsonResponse(reply, "Your vServer #{vps} is being deployed with the image name {image}, root password {pw}".format(
        vps=args[0], image=args[1], pw=''.join(['*' for a in args[2]]))
                               + ('\r\n' if 'intent' in send or 's' in flags else "")
                               + (("Using virtualization type %s" % send['intent']) if 'intent' in send else '')
                               + ("; " if 'intent' in send and 's' in flags else "")
                               + ("Starting VPS after install completes" if 's' in flags else ""))  # TODO that's awful logic control. also fix ' and " differences... everywhere.


flags = HookFlags(p=("plan", True), s="short-plans")
@hook.command("vps stock", flags=flags, doc=("View the stock of each plan in each region.",
                                             "This will be displayed as all the stock under each region, unless -p is specified."
                                             "Flags:",
                                             "\t-p, --plan <name>: Display stock for the plan matching that name",
                                             "\t-s, --short-plans: Display a shortened name for each plan",
                                             "Usage:",
                                             "\t`vps stock'"))
def stock(args, flags):
    reply = centarra("/vps/stock.json")
    if 'p' in flags:
        plan = False
        res = {}
        for region in reply:
            if not plan:
                for plan_amt in reply[region]:
                    if flags['p'] in plan_amt:
                        plan = plan_amt
                        res[region] = reply[region][plan_amt]
                        break
            else:
                res[region] = reply[region][plan]
        return JsonResponse(reply, ("%s: \r\n" % plan) + "\r\n".join(["\t%s: %s" % (i, res[i]) for i in res]))
    return JsonResponse(reply, "")  # TODO


@hook.command("vps nick", args_amt=2, doc=("Sets the nickname of your vps.",
                                           "If your nickname is improperly formatted, it will be cleared.",
                                           "Usage",
                                           "\t`vps nick <vps_id> <nickname>'"))
def nick(args, flags):
    reply = centarra("/vps/%s/setnickname" % args[0], nickname=args[1])
    rpl = "The nickname of vps \"%s\" (#%s) is now set to \"%s\"" % (reply['name'], args[0], reply['nickname'])
    return JsonResponse(reply, rpl)

# I can't figure out if setprofile is needed or not.

@hook.command("vps monitoring", args_amt=2, doc=("Enable or disable 'Watchdog' monitoring on your vServer.",
                                                  "Watchdog monitoring will boot your server back up when it is down.",
                                                  "To enable watchdog monitoring, use the parameter 'enable' - similarly, 'disable' disabled watchdog monitoring.",
                                                  "Usage:",
                                                  "\t`vps monitoring <vps_id> (enable|disable)'"))
def monitoring(args, flags):
    if args not in ['enable', 'disable']:
        return "Invalid monitoring status! - use either 'enable' or 'disable' after the vps_id argument."
    reply = centarra("/vps/%s/monitoring/%s" % (args[0], args[1]))
    return JsonResponse(reply, "Watchdog monitoring is being {enable}d".format(enable=args[1]))  # enabled, disabled.

@hook.command("vps delete", args_amt=1, flags=HookFlags(y='yes'), doc=("Destroy a vServer from your account.",
                                             "This command will erase a vServer, and refund your account the unused balance on the remaining time before renewal.",
                                             "Obviously, this operation is destructive, and will not be recoverable - use with extreme caution.",
                                             "Flags:",
                                             "\t-y, --yes: assume yes to confirmation on deleting your vServer",
                                             "Usage:",
                                             "\t`vps delete <vps_id>'"))
def delete(args, flags):
    print("Are you sure you would like to delete your vServer?")
    line = raw_input('[N/y]: ')
    if line == "y":
        reply = centarra("/vps/%s/delete" % args[0])
        return JsonResponse(reply, "Your vServer has been destroyed.")
    return "Aborted."

@hook.command("vps renew", args_amt=1, doc=("Create a new invoice under your vServer, which will add one month of credit to your expiry date.",
                                            "If you have enough service credit to pay for the invoice, the invoice will be marked as paid automatically.",
                                            "Usage:",
                                            "\t`vps renew <vps_id>'"))
def renew(args, flags):
    reply = centarra("/vps/%s/renew" % args[0])
    if 'invoice_id' in reply:
        return JsonResponse(reply, "A new invoice has been created, ID %s" % reply['invoice_id'])
    return JsonResponse(reply, "A new invoice has been created and paid for with service credit.")

@hook.command("vps boot", args_amt=1, doc=("Boot up a vServer that is currently offline.",
                                           "Usage:",
                                           "\t`vps boot <vps_id>'"))
def create(args, flags):  # I don't know if I should allow specifying a KernelProfile, I don't know where they come from
    reply = centarra("/vps/%s/create" % args[0])
    return JsonResponse(reply, "Your boot is in progress (Job ID: %s)" % reply['job'])

@hook.command("vps rescue", args_amt=1, doc=("Boot your vServer into rescue mode.",  # stolen documentation from Centarra.
                                             "Rescue mode is used to perform manual recovery operations on your VPS,",
                                             "\tsuch as resetting the root password or taking a backup from a compromised machine.",
                                             "Your VPS will be powered off and restarted into the recovery environment.",
                                             "Once you are finished perfoming recovery tasks, simply reboot the VPS through the panel,",
                                             "\tand the normal configuration will take effect.",
                                             "We strongly suggest saving any open files to disk and shutting down any",
                                             "\tdatabase software before launching rescue mode if the VPS is powered on.",
                                             "Usage:",
                                             "\t`vps rescue <vps_id>'"))
def rescue(args, flags):
    reply = centarra("/vps/%s/start-rescue" % args[0])
    return JsonResponse(reply, "Your request to boot into rescue mode has been queued.")

flags = HookFlags(f="forceful")
@hook.command("vps shutdown", flags=flags, args_amt=1, doc=("Shut down your vServer.",
                                               "Flags:",
                                               "\t-f, --forceful: Shut down the server forcefully, using the xl destroy command.",
                                               "Usage:",
                                               "\t`vps shutdown <vps_id>'"))
def shutdown(args, flags):
    cmd = "destroy" if 'f' in flags else "shutdown"
    reply = centarra("/vps/%s/%s" % (args[0], cmd))
    return JsonResponse(reply, "Your request to shutdown has been queued (Job ID: %s)." % reply['job'])

@hook.command("vps powercycle", args_amt=1, doc=("Forcefully power-cycle your vServer",
                                                 "This is equivilent to forcefully shutting your vps down and restarting it.",
                                                 "Usage:",
                                                 "\t`vps powercycle <vps_id>'"))
def powercycle(args, flags):
    reply = centarra("/vps/%s/powercycle" % args[0])
    return JsonResponse(reply, "Your request to powercycle has been queued (Job ID: %s)." % reply['job'])

@hook.command("vps stats", args_amt=4, doc=("A json-only way to access graph data in the panel.",
                                            "Available stats are include netstats, cpustats, and vbdstats.",
                                            "Usage:",
                                            "\t`vps stats <vps_id> (cpustats|netstats|vbdstats) <start> <step>'"))
def stats(args, flags):
    if not args[2] in ["cpustats", "netstats", "vbdstats"]:
        return "Error: your second argument must be the type of graph data you are trying to fetch."
    return centarra("/vps/{}/{}/{}/{}".format(*args))


@hook.command("vps ip", args_amt=lambda x: len(x) >= 2 and len(x) == 2 + {"available": 0, "list": 0, "add": 2, "rdns": 2, "delete": 1}[x[1]],
              doc=("Manage vServer IP addresses.",
                    "This command allows you to modify rDNS records, add new IPs, list current IPs, or delete IP addresses.",
                    "Subcommands:",
                    "\t`available': Display a list of available IP addresses that can be used in the `add' command.",
                    "\t`list': Display a list of current IP addresses attached to your account.",
                    "\t`add': Add a new IP address to your vServer. This required both the net_id from available and the actual address.",
                    "\t`rdns': Set a rDNS record on a specific IP address.",
                    "\t`delete': Remove an IP address permenently from your vServer.",
                    "Usage:",
                    "\t`vps ip <vps_id> (available|list|add <net_id> <ip_addr>|rdns <ip_id> <record_value>|delete <ip_id>)'"))
def ip_manage(args, flags):
    oper = args.pop(1)
    if oper == "add":
        vps_id, net_id, ip = tuple(args)
        reply = centarra("/vps/{}/admin/ip/add".format(vps_id), ipbox="{}!{}".format(net_id, ip))
        # I guess we may as well be nice and check if the IP was adding... otherwise they reached their quota.
        for existing_ip in reply['service']['ips']:
            if existing_ip["ip"] == ip:
                return JsonResponse(reply, "IP address {} was successfully added to your vServer (IP ID {})".format(ip, existing_ip['id']))
        return JsonResponse(reply, "We were unable to add the requested IP address to your vServer. Have you reached your IP quota?")
    elif oper == "rdns":
        vps_id, ip_id, rdns = tuple(args)
        reply = centarra("/vps/{}/admin/ip/{}/rdns-modify".format(vps_id, ip_id), rdns=rdns)
        if not is_valid_host(rdns):
            return JsonResponse(reply, "IP rDNS was likely not set correctly due to malformation in input.")
        return JsonResponse(reply, "IP rDNS was successfully set on your IP address.")
    elif oper == "delete":
        vps_id, ip_id = tuple(args)
        return JsonResponse(centarra("/vps/{}/admin/ip/{}/delete".format(vps_id, ip_id)), "Your IP address has been successfully deleted.")
    elif oper == "list":
        vps_id = args[0]
        reply = centarra("/vps/{}/admin".format(vps_id))
        rpl = []
        for ip in reply['service']['ips']:
            rpl.append("#{}: IPv{} address {} | Broadcast {} | Netmask {} | Gateway {} | Network {}".format(
                ip["id"],
                ip['ipnet']['version'],
                ip['ip'],
                ip['ipnet']['broadcast'],
                ip['ipnet']['netmask'],
                ip['ipnet']['gateway'],
                ip['ipnet']['network']))
        return JsonResponse(reply, "\r\n".join(rpl))
    elif oper == "available":
        vps_id = args[0]
        return "This operation is currently unavailable due to a pending pull request on the panel - we have no way to fetch this information."
    return "Unknown IP operation '{}'.".format(oper)

@hook.command("vps rawstats", args_amt=1)
def rawstats(args, flags):
    return JsonResponse(centarra("/vps/{}/status.json".format(args[0])), "")
