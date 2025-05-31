import os
import pyperclip

def collect_source_files_content(directories, extensions=('.py', '.cpp', '.c', '.h')):
    all_contents = []

    for directory in directories:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(extensions):
                    filepath = os.path.join(root, file)
                    try:
                        print(f' readin file: {filepath}')
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        entry = f"// ===== {filepath} =====\n{content}\n"
                        all_contents.append(entry)
                    except Exception as e:
                        print(f"⚠️ Nie udało się odczytać {filepath}: {e}")

    return "\n".join(all_contents)

def copy_sources_to_clipboard(directories):
    combined_content = collect_source_files_content(directories)
    pyperclip.copy(combined_content)
    print("📋 Skopiowano do schowka!")

if __name__ == '__main__':
    dirs_to_scan = [
        './praetorian_binance_backtester/bin/',
        './praetorian_binance_backtester/core/',

        './Praetorian-Strategies/praetorian_strategies/core/',
        './Praetorian-Strategies/praetorian_strategies/strategies/',

        './Legatus-Binance-Deputy/legatus_binance_deputy/bin/',
        './Legatus-Binance-Deputy/legatus_binance_deputy/core/',
        './Legatus-Binance-Deputy/legatus_binance_deputy/enums/',
    ]
    copy_sources_to_clipboard(dirs_to_scan)