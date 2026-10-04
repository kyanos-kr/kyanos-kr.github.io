"""
KYANOS Market Pulse - Console TUI Monitor
Terminal-based realtime monitor with ANSI color.
"""
import os
import sys
import time

# UTF-8 stdout configuration
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from market_data import get_all_market_data

# ANSI Color Codes
RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[91m"     # 상승 (한국식)
BLUE = "\033[94m"    # 하락 (한국식)
GRAY = "\033[90m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
GREEN = "\033[92m"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def format_row(name, symbol, price_str, change_str, rate_str, status):
    if status == 'up':
        color = RED
        arrow = "▲"
    elif status == 'down':
        color = BLUE
        arrow = "▼"
    else:
        color = GRAY
        arrow = "-"
        
    name_display = f"{name} ({symbol})"[0:16]
    return f"{name_display:<18} | {price_str:>14} | {color}{arrow} {change_str:>12} ({rate_str:>7}){RESET}"

def run_console_loop():
    print(f"{CYAN}키아노스 마켓 펄스 콘솔 모니터를 시작합니다... (종료: Ctrl+C){RESET}")
    time.sleep(1)
    
    while True:
        try:
            data = get_all_market_data()
            clear_screen()
            
            print(f"{BOLD}{CYAN}========================================================================={RESET}")
            print(f"{BOLD}  🏛️ 키아노스 마켓 펄스 (KYANOS Market Pulse) - 실시간 시세 모니터{RESET}")
            print(f"  기준 일시: {data['timestamp']} | 갱신 주기: 5초 | 100% 무료 공개 데이터")
            print(f"{BOLD}{CYAN}========================================================================={RESET}")
            
            # 1. 암호화폐
            print(f"\n{BOLD}{YELLOW}🪙 주요 암호화폐 (업비트 KRW){RESET}")
            print("-" * 65)
            for item in data['crypto']:
                print(format_row(item['name'], item['symbol'], item['price_str'], item['change_str'], item['change_rate_str'], item['status']))
                
            # 2. 국내 증시 및 환율
            print(f"\n{BOLD}{GREEN}📈 국내 증시 & 환율 (네이버 증권){RESET}")
            print("-" * 65)
            for item in data['domestic']:
                print(format_row(item['name'], item['symbol'], item['price_str'], item['change_str'], item['change_rate_str'], item['status']))
                
            # 3. 글로벌 증시 & 테크
            print(f"\n{BOLD}{CYAN}🌐 글로벌 증시 & 빅테크 (야후 파이낸스){RESET}")
            print("-" * 65)
            for item in data['global']:
                print(format_row(item['name'], item['symbol'], item['price_str'], item['change_str'], item['change_rate_str'], item['status']))
                
            # 4. 귀금속 & 실물 원자재 (금·은)
            print(f"\n{BOLD}{YELLOW}🥇 실물 귀금속 & 원자재 (금·은 / 야후 파이낸스){RESET}")
            print("-" * 65)
            for item in data['metals']:
                print(format_row(item['name'], item['symbol'], item['price_str'], item['change_str'], item['change_rate_str'], item['status']))
                
            print("\n" + "-" * 65)
            print(f"{GRAY}화면을 종료하려면 Ctrl+C 를 누르세요.{RESET}")
            
            time.sleep(5)
        except KeyboardInterrupt:
            print("\n모니터링을 종료합니다.")
            break
        except Exception as e:
            print(f"\n[오류 발생] 잠시 후 재시도합니다: {e}")
            time.sleep(5)

if __name__ == '__main__':
    run_console_loop()
