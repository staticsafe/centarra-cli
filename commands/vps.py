from utils import hook, HookFlags, JsonResponse
from libs import centarra, substitutes, sub

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

@hook.command("vps available", args_amt=1, flags=flags, doc=("View available vServers that are currently being sold, as well as available regions.",
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
    if args[0] == "regions":
        return JsonResponse(reply['regions'], '\r\n'.join(["(%s): %s" % (i['id'], i['name']) for i in reply['regions']]))
    else:
        rpl = []
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
                                             "\t`vps signup $Dallas \"$TortoiseCloud 256\"' (after viewing available plans)"))
def signup(args, flags):
    reply = centarra('/vps/signup', plan=args[0], region=args[1])
    sub(reply['name'], reply['id'], False)
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


@hook.command("vps templates", args_amt=1, doc=("Display all vps templates available for deployment",
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
@hook.command("vps deploy", doc=("Deploy your vps with an image so you can start it up.",
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
