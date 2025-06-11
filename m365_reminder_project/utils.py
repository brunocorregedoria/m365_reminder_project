from datetime import datetime, timedelta


# Função para detectar conflitos de horário entre eventos
def detect_conflicts(events):
    conflicts = []
    # Ordena os eventos por data de início para facilitar a detecção de conflitos
    sorted_events = sorted(events, key=lambda x: x.start_datetime)

    # Itera sobre os eventos para comparar cada um com os eventos subsequentes
    for i in range(len(sorted_events)):
        for j in range(i + 1, len(sorted_events)):
            event1 = sorted_events[i]
            event2 = sorted_events[j]

            # Verifica se há sobreposição de horários entre os dois eventos
            # Um conflito ocorre se o início do segundo evento for antes do fim do primeiro
            # E o fim do primeiro evento for depois do início do segundo
            if max(event1.start_datetime, event2.start_datetime) < min(
                event1.end_datetime, event2.end_datetime
            ):
                conflicts.append(
                    (event1, event2)
                )  # Adiciona o par de eventos conflitantes à lista
    return conflicts


# Função para sugerir blocos de tempo livre para foco
def suggest_focus_blocks(
    events, start_hour=9, end_hour=17, min_block_duration_minutes=60
):
    today = datetime.now().date()
    # Define o início e o fim do horário de trabalho para o dia atual
    work_start = datetime(today.year, today.month, today.day, start_hour, 0, 0)
    work_end = datetime(today.year, today.month, today.day, end_hour, 0, 0)

    busy_intervals = []
    # Converte os eventos em intervalos de tempo ocupados
    for event in events:
        # Ajusta os horários dos eventos para a data de hoje para comparação
        event_start_today = datetime(
            today.year,
            today.month,
            today.day,
            event.start_datetime.hour,
            event.start_datetime.minute,
            event.start_datetime.second,
        )
        event_end_today = datetime(
            today.year,
            today.month,
            today.day,
            event.end_datetime.hour,
            event.end_datetime.minute,
            event.end_datetime.second,
        )
        busy_intervals.append((event_start_today, event_end_today))

    # Ordena os intervalos ocupados e mescla aqueles que se sobrepõem
    busy_intervals.sort()
    merged_intervals = []
    if busy_intervals:
        current_start, current_end = busy_intervals[0]
        for i in range(1, len(busy_intervals)):
            next_start, next_end = busy_intervals[i]
            if next_start <= current_end:
                current_end = max(current_end, next_end)
            else:
                merged_intervals.append((current_start, current_end))
                current_start, current_end = next_start, next_end
        merged_intervals.append((current_start, current_end))

    focus_blocks = []
    current_time = work_start

    # Encontra os blocos de tempo livre entre os intervalos ocupados
    for busy_start, busy_end in merged_intervals:
        # Garante que o intervalo ocupado esteja dentro do horário de trabalho
        busy_start = max(busy_start, work_start)
        busy_end = min(busy_end, work_end)

        if busy_start > current_time:
            block_duration = busy_start - current_time
            # Verifica se o bloco de tempo livre é maior que a duração mínima configurada
            if block_duration.total_seconds() >= min_block_duration_minutes * 60:
                focus_blocks.append((current_time, busy_start))
        current_time = max(current_time, busy_end)

    # Verifica o tempo livre após o último evento ocupado até o fim do dia de trabalho
    if work_end > current_time:
        block_duration = work_end - current_time
        if block_duration.total_seconds() >= min_block_duration_minutes * 60:
            focus_blocks.append((current_time, work_end))

    return focus_blocks
