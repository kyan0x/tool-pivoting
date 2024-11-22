import socket
import argparse
from concurrent.futures import ThreadPoolExecutor
from rich.console import Console
import ipaddress

def is_ip_active(ip, port, timeout):
    try:
        sock = socket.create_connection((ip, port), timeout=timeout)
        sock.close()
        return True
    except socket.error:
        return False

def process_ip_range(ip_range):
    try:
        network = ipaddress.IPv4Network(ip_range, strict=False)
        return [str(ip) for ip in network.hosts()]
    except ValueError:
        return []

def main():
    console = Console()

    console.print(r"""[purple]
                 _-.                       .-_ 
              _..-'(                       )`-.._
           ./'. '||\         (\_/)       .//||` .` 
        ./'.|'.'||||\|..     )*.*(    ..|//||||`.`|.`   
     ./'..|'.|| |||||\```````  "  '''''''/||||| ||.`|..`\      [white]developed by kyan[/]
   ./'.||'.|||| ||||||||||||.     .|||||||||||| ||||.`||.`\     [red]use -h for open menu help[/]
  /'|||'.|||||| ||||||||||||{     }|||||||||||| ||||||.`|||` 
 '.|||'.||||||| ||||||||||||{     }|||||||||||| |||||||.`|||.`    
'.||| ||||||||| |/'   ``\||/`     '\||/''   `\| ||||||||| |||.` 
|/' \ /'     `\ /          |/\   /\|          \ /'     `\ / `\| 
V    V         V          }' `\ /' `{          V         V    V 
`    `         `               U               '         '     
[/]""")
    parser = argparse.ArgumentParser(description="Verifica IPs na rede via TCP")
    parser.add_argument("-i", "--ip", help="Endereço IP ou faixa de IP (ex: 192.168.1.0/24, 192.168.1.100)")
    parser.add_argument("-p", "--port", type=int, default=80, help='Insira a porta (ex: 80, 443 default 80)')
    parser.add_argument("-t", "--timeout", type=float, default=1, help="Insira o timeout (ex: 1, 10, 20 default: 1)")
    parser.add_argument("-w", "--workers", type=int, default=10, help="Insira a quantidade de workers (default: 10)")
    args = parser.parse_args()

    ips = process_ip_range(args.ip)

    if not ips:
        console.print("[white][INFO][/][bold red] Não foi possível processar os IPs.[/bold red]")
        return

    active_ips = []

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        with console.status("[bold yellow]Verificando IPs ativos...[/bold yellow]") as status:
            results = executor.map(is_ip_active, ips, [args.port] * len(ips), [args.timeout] * len(ips))

            active_ips_count = 0
            inactive_ips_count = 0

            for ip, is_active in zip(ips, results):
                if is_active:
                    active_ips_count += 1
                    active_ips.append(ip)
                    console.print(f"[white][INFO][/][bold green] {ip} está ativo[/bold green]")
                else:
                    inactive_ips_count += 1

            console.print('[INFO] {} foram testados, [bold green]{} estão ativos[/bold green] e [red]{} estão desativados[/]'.format(len(ips), active_ips_count, inactive_ips_count))

if __name__ == "__main__":
    main()