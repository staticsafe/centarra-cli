from utils import hook, HookFlags, JsonResponse
from libs import centarra, substitutes, dump_subs

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
        if not i['name'] in substitutes:
            substitutes[i['name']] = [str(i['id']), False]
        if not i['nickname'] in substitutes:
            substitutes[i['nickname']] = [str(i['id']), False]
    dump_subs()
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

@hook.command("vps available", args_amt=1, doc=("View available vServers that are currently being sold, as well as available regions.",
                                                "All of the available plans are available here - however, see `vps stock' for information on region stock.",
                                                "There are two subcommands available:",
                                                "\tregions: Display regions Centarra supports.",
                                                "\tplans: Display information on plans available for purchase in these regions. This includes plan ID, name, and price (in USD) by default",
                                                "Flags (`plans' subcommand only):",
                                                "\t-l, --ip-limits: Display IPv4 and IPv6 limits on a certain plan",
                                                "\t-b, --btc-price: Display the price of a plan in BTC",
                                                "\t-S, --swap: Display the amount of swap that would be allocated to this plan",
                                                "\t-M, --memory: Display the amount of memory this plan would be allocated (also included in plan names)",
                                                "\t-D, --disk: Display the disk space allocated to this plan"))
def available(args, flags):
    reply = centarra('/vps/signup')
    for i in reply['regions']:
        if not i['name'] in substitutes:
            substitutes[i['name']] = [str(i['id']), False]
    for i in reply['resource_plans']:
        if not i['name'] in substitutes:
            substitutes[i['name']] = [str(i['id']), False]
    dump_subs()
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
