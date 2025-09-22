from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QProgressBar, QScrollArea, QFrame,
    QTreeWidget, QTreeWidgetItem, QCheckBox, QSpinBox, QSpacerItem,
    QSizePolicy, QDialog, QComboBox
)
from PySide6.QtCore import Qt, QTimer, QTime
import multiprocessing
import psutil
import platform
import sys
import time
import threading

# ---------------- FUNÇÕES ----------------
def thread_worker(memoria, cpu_consume, evento_pause):
    """Thread que consome CPU e memória opcionalmente"""
    while True:
        evento_pause.wait()  # Aguarda se estiver pausado
        if cpu_consume:
            for _ in range(1000000):
                pass
        time.sleep(0.1)

def processo_real(memoria_mb, threads, cpu_consume, evento_pause):
    memoria = bytearray(memoria_mb * 1024 * 1024)
    for i in range(0, len(memoria), 4096):
        memoria[i] = 1

    workers = []
    for _ in range(threads):
        t = threading.Thread(target=thread_worker, args=(memoria, cpu_consume, evento_pause), daemon=True)
        t.start()
        workers.append(t)

    while True:
        evento_pause.wait()  # Mantém o processo vivo, respeitando pausa
        time.sleep(0.5)

# ---------------- CLASSES ----------------
class ProcessoSO:
    pid_counter = 1
    def __init__(self, nome, memoria, threads, cpu_consume, prioridade):
        self.nome = nome
        self.memoria_mb = memoria
        self.threads = threads
        self.cpu_consume = cpu_consume
        self.prioridade = prioridade
        self.estado = "Pronto"
        self.progress = 0
        self.inicio = time.time()
        self.logs = [f"{self.hora()} - Processo criado"]
        self.evento_pause = multiprocessing.Event()
        self.evento_pause.set()  # Começa ativo
        self.process = multiprocessing.Process(target=processo_real, args=(memoria, threads, cpu_consume, self.evento_pause))
        self.process.start()
        self.pid = self.process.pid
        self.ps = psutil.Process(self.pid)
        ProcessoSO.pid_counter += 1

    def hora(self):
        return QTime.currentTime().toString("HH:mm:ss")

    def atualizar_estado(self):
        if self.process.is_alive():
            self.estado = "Rodando" if self.evento_pause.is_set() else "Pausado"
            self.progress = min(self.progress + self.threads, 100)
        else:
            if self.estado != "Finalizado":
                self.logs.append(f"{self.hora()} - Processo finalizado")
            self.estado = "Finalizado"
            self.progress = 100

    def tempo_execucao(self):
        return int(time.time() - self.inicio)

    def pausar(self):
        if self.process.is_alive():
            self.evento_pause.clear()
            self.estado = "Pausado"

    def retomar(self):
        if self.process.is_alive():
            self.evento_pause.set()
            self.estado = "Rodando"

    def terminar(self):
        if self.process.is_alive():
            self.process.terminate()
            self.process.join()
        self.estado = "Finalizado"
        self.progress = 100
        self.logs.append(f"{self.hora()} - Processo encerrado")

# ---------------- CONFIGURAÇÃO DO PC ----------------
class ConfigPC(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuração do PC")
        self.setMinimumSize(400, 350)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        sys_info = [
            f"Sistema: {platform.system()} {platform.release()}",
            f"Plataforma: {platform.platform()}",
            f"Processador: {platform.processor()}",
            f"Núcleos Físicos: {psutil.cpu_count(logical=False)}",
            f"Núcleos Lógicos: {psutil.cpu_count(logical=True)}",
            f"Frequência CPU: {psutil.cpu_freq().current:.2f} MHz",
        ]
        mem = psutil.virtual_memory()
        sys_info += [
            f"Memória Total: {mem.total//(1024**2)} MB",
            f"Memória Disponível: {mem.available//(1024**2)} MB"
        ]
        disk = psutil.disk_usage('/')
        sys_info += [
            f"Disco Total: {disk.total//(1024**3)} GB",
            f"Disco Usado: {disk.used//(1024**3)} GB"
        ]

        for info in sys_info:
            lbl = QLabel(info)
            lbl.setStyleSheet("font-size:12px; color:#ddd;")
            layout.addWidget(lbl)

        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

# ---------------- DASHBOARD ----------------
class DashboardCompleto(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulador de Processos - Task Manager")
        self.setMinimumSize(1000, 650)
        self.processos = []

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10,10,10,10)
        main_layout.setSpacing(15)

        # ---------------- CONTROLES ----------------
        control_layout = QVBoxLayout()
        main_layout.addLayout(control_layout, 1)

        self.input_nome = QLineEdit()
        self.input_nome.setPlaceholderText("Nome do processo")
        self.input_memoria = QLineEdit()
        self.input_memoria.setPlaceholderText("Memória (MB)")
        self.spin_threads = QSpinBox()
        self.spin_threads.setRange(1, 16)
        self.spin_threads.setValue(1)
        self.spin_threads.setPrefix("Threads: ")
        self.chk_cpu = QCheckBox("Consumir CPU")
        self.chk_cpu.setChecked(True)
        self.combo_prioridade = QComboBox()
        self.combo_prioridade.addItems(["Baixa", "Média", "Alta"])
        self.btn_add = QPushButton("Adicionar Processo")
        self.btn_add.clicked.connect(self.novo_processo)
        self.btn_config = QPushButton("Configuração do PC")
        self.btn_config.clicked.connect(self.abrir_config)

        for w in [self.input_nome, self.input_memoria, self.spin_threads, self.chk_cpu, self.combo_prioridade, self.btn_add, self.btn_config]:
            control_layout.addWidget(w)

        # ---------------- BARRAS EM TEMPO REAL ----------------
        self.label_cpu = QLabel("CPU: 0%")
        self.bar_cpu = QProgressBar()
        self.bar_cpu.setTextVisible(False)
        self.bar_cpu.setFixedHeight(6)

        self.label_mem = QLabel("Memória: 0%")
        self.bar_mem = QProgressBar()
        self.bar_mem.setTextVisible(False)
        self.bar_mem.setFixedHeight(6)

        self.label_disk = QLabel("Disco: 0%")
        self.bar_disk = QProgressBar()
        self.bar_disk.setTextVisible(False)
        self.bar_disk.setFixedHeight(6)

        self.label_net = QLabel("Rede: 0 KB/s")
        self.bar_net = QProgressBar()
        self.bar_net.setTextVisible(False)
        self.bar_net.setFixedHeight(6)

        for lbl, bar in [(self.label_cpu, self.bar_cpu), (self.label_mem, self.bar_mem),
                         (self.label_disk, self.bar_disk), (self.label_net, self.bar_net)]:
            control_layout.addWidget(lbl)
            control_layout.addWidget(bar)

        control_layout.addStretch()

        # ---------------- LISTA DE PROCESSOS ----------------
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(5)
        self.scroll.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll, 2)

        # ---------------- REDE INICIAL ----------------
        self.net_last = psutil.net_io_counters()
        self.timer = QTimer()
        self.timer.timeout.connect(self.atualizar_dashboard)
        self.timer.start(1000)

    # ---------------- FUNÇÕES ----------------
    def novo_processo(self):
        nome = self.input_nome.text() or f"Proc{len(self.processos)+1}"
        try:
            memoria = int(self.input_memoria.text() or 50)
            threads = self.spin_threads.value()
            cpu_consume = self.chk_cpu.isChecked()
            prioridade = self.combo_prioridade.currentText()
        except ValueError:
            return
        p = ProcessoSO(nome, memoria, threads, cpu_consume, prioridade)
        self.processos.append(p)
        self.atualizar_dashboard()

    def abrir_config(self):
        dlg = ConfigPC()
        dlg.exec()

    # ---------------- DASHBOARD ATUALIZADO ----------------
    def atualizar_dashboard(self):
        # Barras gerais
        cpu = psutil.cpu_percent()
        self.bar_cpu.setValue(int(cpu))
        self.label_cpu.setText(f"CPU: {cpu}%")

        mem = psutil.virtual_memory()
        self.bar_mem.setValue(int(mem.percent))
        self.label_mem.setText(f"Memória: {mem.percent}%")

        disk = psutil.disk_usage('/')
        self.bar_disk.setValue(int(disk.percent))
        self.label_disk.setText(f"Disco: {disk.percent}%")

        net_now = psutil.net_io_counters()
        upload = (net_now.bytes_sent - self.net_last.bytes_sent)/1024
        download = (net_now.bytes_recv - self.net_last.bytes_recv)/1024
        self.bar_net.setValue(min(int(upload + download), 100))
        self.label_net.setText(f"Rede: ↑{upload:.1f} KB/s ↓{download:.1f} KB/s")
        self.net_last = net_now

        # Limpa lista de processos
        for i in reversed(range(self.scroll_layout.count())):
            w = self.scroll_layout.itemAt(i).widget()
            if w:
                w.setParent(None)

        # Novos processos no topo
        for p in reversed(self.processos):
            try:
                if p.process.is_alive():
                    p.atualizar_estado()
                    mem_mb = p.ps.memory_info().rss // 1024 // 1024
                    threads_real = p.threads
                    thread_ids = [f"T{i+1}" for i in range(p.threads)]
                else:
                    p.estado = "Finalizado"
                    mem_mb = 0
                    threads_real = 0
                    thread_ids = []
            except psutil.NoSuchProcess:
                p.estado = "Finalizado"
                mem_mb = 0
                threads_real = 0
                thread_ids = []

            # Frame do processo
            frame = QFrame()
            frame.setFrameShape(QFrame.StyledPanel)
            frame.setFixedHeight(180)
            frame.setStyleSheet(
                "QFrame {background-color: #3c4145; border-radius: 6px; padding: 6px;}"
                "QFrame:hover {background-color: #3c4145;}"
            )
            layout = QVBoxLayout(frame)
            layout.setSpacing(3)

            # Linha principal
            top_layout = QHBoxLayout()
            lbl_nome = QLabel(f"{p.nome} (PID {p.pid})")
            lbl_nome.setStyleSheet("font-weight: bold; font-size:12px; color:#ddd;")

            cor_estado = "#ddd"
            if p.estado == "Pronto": cor_estado = "#888888"
            elif p.estado == "Rodando": cor_estado = "#3498db"
            elif p.estado == "Pausado": cor_estado = "#f39c12"
            elif p.estado == "Finalizado": cor_estado = "#2ecc71"
            lbl_estado = QLabel(f"{p.estado} | Mem: {mem_mb} MB | Threads: {threads_real} | Tempo: {p.tempo_execucao()}s")
            lbl_estado.setStyleSheet(f"font-size:11px; color: {cor_estado};")

            cor_prioridade = "#3498db"
            if p.prioridade == "Média": cor_prioridade = "#e67e22"
            elif p.prioridade == "Alta": cor_prioridade = "#e74c3c"
            lbl_prioridade = QLabel(f"Prioridade: {p.prioridade}")
            lbl_prioridade.setStyleSheet(f"font-size:11px; font-weight:bold; color:{cor_prioridade};")

            btn_terminar = QPushButton("⨉")
            btn_terminar.setFixedSize(18,18)
            btn_terminar.setStyleSheet("font-size:11px;")
            def criar_terminar(proc=p, fr=frame):
                def terminar():
                    proc.terminar()
                    fr.setParent(None)
                    if proc in self.processos:
                        self.processos.remove(proc)
                return terminar
            btn_terminar.clicked.connect(criar_terminar())

            # Botão Pausar/Retomar
            btn_pausar = QPushButton("⏸/▶")
            btn_pausar.setFixedSize(28,18)
            def criar_pause_resume(proc=p):
                def toggle():
                    if proc.estado == "Rodando":
                        proc.pausar()
                    elif proc.estado == "Pausado":
                        proc.retomar()
                return toggle
            btn_pausar.clicked.connect(criar_pause_resume())

            top_layout.addWidget(lbl_nome)
            top_layout.addStretch()
            top_layout.addWidget(lbl_estado)
            top_layout.addWidget(lbl_prioridade)
            top_layout.addWidget(btn_pausar)
            top_layout.addWidget(btn_terminar)
            layout.addLayout(top_layout)

            # Barra de progresso
            progress = QProgressBar()
            progress.setValue(p.progress)
            progress.setFixedHeight(8)
            progress.setStyleSheet(
                "QProgressBar {border: 1px solid #aaa; border-radius: 4px; background-color: #ddd;}"
                "QProgressBar::chunk {background-color: #3498db; border-radius: 4px;}"
            )
            progress.setTextVisible(False)
            layout.addWidget(progress)

            # Threads detalhadas
            if thread_ids:
                tree = QTreeWidget()
                tree.setHeaderLabels(["Thread ID"])
                max_tree_height = 120
                tree.setMaximumHeight(max_tree_height)
                tree.setVerticalScrollMode(QTreeWidget.ScrollPerPixel)
                tree.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                tree.setStyleSheet(
                    """
                    QTreeWidget {background-color: #3c4145; border: 1px solid #aaa; border-radius: 4px;}
                    QHeaderView::section {background-color: #3c4145; border: none;}
                    QTreeWidget::item {background-color: #3c4145; color: #ddd; padding: 2px;}
                    QTreeWidget::item:selected {background-color: #3c4145; color: white;}
                    QTreeView::branch {background: #3c4145;}
                    QScrollBar:vertical {width: 6px; background: #2c2f33; margin: 2px 0 2px 0; border-radius: 3px;}
                    QScrollBar::handle:vertical {background: #3498db; min-height: 10px; border-radius: 3px;}
                    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {height: 0px;}
                    """
                )
                for tid in thread_ids:
                    QTreeWidgetItem(tree, [str(tid)])
                layout.addWidget(tree)

            # Adiciona frame no topo
            self.scroll_layout.insertWidget(0, frame)

        self.scroll_layout.addStretch()

# ---------------- EXECUÇÃO ----------------
if __name__ == "__main__":
    multiprocessing.set_start_method("spawn")
    app = QApplication(sys.argv)
    window = DashboardCompleto()
    window.show()
    sys.exit(app.exec())
