import tkinter as tk
import traceback
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from color import Color  # GRAY, WHITE, BLACK, BUTTON, FOCUS 등
import socket
import threading
import json
import datetime

# 전역 데이터
employees_data = []  # 직원 목록 (dict 리스트)
chatrooms_data = []  # 채팅방 목록 (dict 리스트)

test_socket = None

class ChattingFrame(tk.Frame):
    def __init__(self, root, sock):
        super().__init__(root, width=350, height=730, bg=Color.WHITE)
        self.root = root
        self.sock = sock
        self.current_chat_target = None
        self.current_room_id = None

        self.fr_top = tk.Frame(self, width=350, height=130, bg=Color.GRAY)
        self.fr_top.grid(row=0, column=0, sticky="nsew")
        self.fr_top.grid_propagate(False)
        self.create_top_frame()

        self.fr_middle = tk.Frame(self, width=350, height=560, bg=Color.WHITE, bd=1, relief=tk.SOLID)
        self.fr_middle.grid(row=1, column=0, sticky="nsew")
        self.fr_middle.grid_propagate(False)
        self.fr_main = tk.Frame(self.fr_middle, bg=Color.WHITE)
        self.fr_chatList = tk.Frame(self.fr_middle, bg=Color.WHITE)
        self.fr_group = tk.Frame(self.fr_middle, bg=Color.WHITE)
        self.fr_chat = tk.Frame(self.fr_middle, bg=Color.WHITE)
        for frame in (self.fr_main, self.fr_chatList, self.fr_group, self.fr_chat):
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.fr_bottom = tk.Frame(self, width=350, height=60, bg=Color.WHITE)
        self.fr_bottom.grid(row=2, column=0, sticky="nsew")
        self.fr_bottom.grid_propagate(False)
        self.create_bottom_buttons()

        self.show_main()

    def create_top_frame(self):
        self.fr_top_user = tk.Frame(self.fr_top, bg=Color.GRAY, height=60)
        self.fr_top_user.pack(fill=tk.X, side=tk.TOP)
        self.lbl_employee = tk.Label(
            self.fr_top_user,
            text=self.root.get_user_id(),
            font=('맑은 고딕', 16, 'bold'),
            fg=Color.BLACK,
            bg=Color.GRAY
        )
        self.lbl_employee.pack(pady=(10, 0))
        self.lbl_name = tk.Label(
            self.fr_top_user,
            text=self.root.get_user_name(),
            font=('맑은 고딕', 14),
            fg=Color.BLACK,
            bg=Color.GRAY
        )
        self.lbl_name.pack(pady=(0, 10))

        self.fr_top_search = tk.Frame(self.fr_top, bg=Color.GRAY, height=70)
        self.fr_top_search.pack(fill=tk.BOTH, expand=True, side=tk.TOP)
        self.search_entry = tk.Entry(self.fr_top_search, font=('맑은 고딕', 12), relief=tk.GROOVE, bd=2)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=10)
        self.search_btn = tk.Button(
            self.fr_top_search,
            text="🔍",
            font=('맑은 고딕', 12),
            bg=Color.BUTTON,
            fg=Color.WHITE,
            relief="flat",
            activebackground=Color.FOCUS,
            command=self.search_employees
        )
        self.search_btn.pack(side=tk.RIGHT, padx=10, pady=10)
    def create_bottom_buttons(self):
        for widget in self.fr_bottom.winfo_children():
            widget.destroy()
        btn_main = tk.Button(self.fr_bottom, text="메인", font=('맑은 고딕', 12, 'bold'),
                             bg="#333333", fg=Color.WHITE, relief="flat", activebackground="#2a2a2a",
                             command=self.show_main)
        btn_chatList = tk.Button(self.fr_bottom, text="채팅방목록", font=('맑은 고딕', 12, 'bold'),
                                 bg="#444444", fg=Color.WHITE, relief="flat", activebackground="#3b3b3b",
                                 command=self.show_chatlist)
        btn_group = tk.Button(self.fr_bottom, text="채팅방 만들기", font=('맑은 고딕', 12, 'bold'),
                              bg="#555555", fg=Color.WHITE, relief="flat", activebackground="#4a4a4a",
                              command=self.show_group)
        btn_main.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        btn_chatList.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        btn_group.grid(row=0, column=2, sticky="nsew", padx=0, pady=0)
        for i in range(3):
            self.fr_bottom.columnconfigure(i, weight=1)
        self.fr_bottom.rowconfigure(0, weight=1)
    def show_main(self):
        self.fr_main.lift()
        req = {"code": 85010, "args": {"사원이름": self.search_entry.get()}}
        self.send_(json.dumps(req, ensure_ascii=False))
    def show_chatlist(self):
        self.fr_chatList.lift()
        req = {"code": 85014, "args": {}}
        self.send_(json.dumps(req, ensure_ascii=False))
    def show_group(self):
        self.fr_group.lift()
        self.update_group()
    def show_chat(self, room_id, chat_target):
        self.current_room_id = int(room_id)
        self.current_chat_target = chat_target
        self.fr_chat.lift()
        self.update_chat()
        # 채팅방에 들어갈 때, 이전 채팅 내역을 불러옵니다.
        self.load_chat_history()
        self.chat_history.see("end")
    def update_main(self, employees=None):
        # 기존 fr_main 내 위젯 제거
        for widget in self.fr_main.winfo_children():
            widget.destroy()

        # Treeview와 스크롤바를 담을 컨테이너 프레임 생성
        container = tk.Frame(self.fr_main)
        container.pack(fill=tk.BOTH, expand=True)

        # Treeview 생성
        tree = ttk.Treeview(container, columns=("사원코드", "이름", "부서", "직급"), show="headings")
        tree.heading("사원코드", text="사원코드")
        tree.heading("이름", text="이름")
        tree.heading("부서", text="부서")
        tree.heading("직급", text="직급")
        tree.column("사원코드", width=80, anchor="center")
        tree.column("이름", width=80, anchor="center")
        tree.column("부서", width=80, anchor="center")
        tree.column("직급", width=80, anchor="center")
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 수직 스크롤바 생성 및 연결
        scrollbar = tk.Scrollbar(container, orient="vertical", command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scrollbar.set)

        print("받은 직원 목록:", employees_data)
        data = employees if employees is not None else employees_data
        print("뭐한 목록:", data)
        for emp in data:
            tree.insert("", tk.END, values=(
                emp.get("사원코드"), emp.get("사원명"), emp.get("소속부서"), emp.get("직급")))
        tree.bind("<Double-1>", lambda e: self.open_one_to_one_chat(tree))
    def search_employees(self):
        self.show_main()
    def open_one_to_one_chat(self, tree):
        selected = tree.selection()
        if selected:
            values = tree.item(selected[0], "values")
            target_emp_code = values[0]
            personal_room_name = f"개인톡: {values[1]}"
            existing = [room for room in chatrooms_data if room.get("room_name") == personal_room_name]
            if existing:
                room_id = existing[0].get("room_id")
                self.show_chat(room_id, personal_room_name)
            else:
                req = {
                    "code": 85012,
                    "args": {
                        "room_name": personal_room_name,
                        "members": [target_emp_code, self.root.id_]
                    }
                }
                print(req)
                self.send_(json.dumps(req, ensure_ascii=False))
    def update_group(self):
        # 기존 fr_group 내 위젯 초기화
        for widget in self.fr_group.winfo_children():
            widget.destroy()

        # 타이틀 라벨
        lbl = tk.Label(self.fr_group, text="단체 채팅방 만들기 - 초대할 사람 선택",
                       font=('맑은 고딕', 12, 'bold'), bg=Color.WHITE, fg=Color.BLACK)
        lbl.pack(pady=5)

        # 채팅방 이름 입력용 Entry (작은 크기, 플레이스홀더 텍스트 추가)
        self.custom_room_name_entry = tk.Entry(self.fr_group, font=('맑은 고딕', 10), width=30, relief=tk.GROOVE, bd=1)
        self.custom_room_name_entry.insert(0, "단체방 이름을 입력하세요")
        # 포커스 들어갈 때 플레이스홀더 삭제, 포커스 아웃 시 빈 경우 다시 추가
        self.custom_room_name_entry.bind("<FocusIn>", self.clear_placeholder)
        self.custom_room_name_entry.bind("<FocusOut>", self.add_placeholder)
        self.custom_room_name_entry.pack(pady=5)

        # 스크롤 가능한 컨테이너: 높이는 200, 너비는 300으로 고정 (필요에 따라 조정)
        container = tk.Frame(self.fr_group, bg=Color.WHITE, height=300, width=300)
        container.pack(pady=5)
        container.pack_propagate(False)  # 자식 위젯에 맞춰 크기 변경 방지

        # 캔버스 생성: 너비를 약간 줄여서 스크롤바가 보이도록 설정
        canvas = tk.Canvas(container, bg=Color.WHITE, highlightthickness=0, width=280)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 세로 스크롤바 추가
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=scrollbar.set)

        # 캔버스 내부에 체크박스들을 담을 프레임 생성
        inner_frame = tk.Frame(canvas, bg=Color.WHITE)
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")

        # inner_frame 크기 변경 시 캔버스 scrollregion 업데이트
        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        inner_frame.bind("<Configure>", on_configure)

        # 직원 목록 기반 체크박스 생성
        self.group_vars = {}
        for emp in employees_data:
            var = tk.IntVar()
            self.group_vars[emp["사원코드"]] = var
            chk = tk.Checkbutton(inner_frame, text=f"{emp['사원명']} ({emp['소속부서']})",
                                 variable=var, bg=Color.WHITE, fg=Color.BLACK)
            chk.pack(anchor="w", padx=10)

        # 채팅방 생성 버튼
        btn_create = tk.Button(self.fr_group, text="채팅방 만들기", font=('맑은 고딕', 12, 'bold'),
                               bg=Color.BUTTON, fg=Color.WHITE, relief="flat",
                               activebackground=Color.FOCUS, command=self.create_group_chat)
        btn_create.pack(pady=10)
    def clear_placeholder(self, event):
        if self.custom_room_name_entry.get() == "단체방 이름을 입력하세요":
            self.custom_room_name_entry.delete(0, tk.END)
    def add_placeholder(self, event):
        if not self.custom_room_name_entry.get():
            self.custom_room_name_entry.insert(0, "단체방 이름을 입력하세요")
    def create_group_chat(self):
        # 선택된 사원코드 리스트 생성 (체크된 항목만)
        selected_members = [emp["사원코드"] for emp in employees_data if self.group_vars[emp["사원코드"]].get() == 1]
        # 현재 사용자의 ID가 목록에 없다면 자동으로 추가 (채팅방 생성자는 항상 참여되어야 함)
        if self.root.id_ not in selected_members:
            selected_members.append(self.root.id_)

        if not selected_members:
            messagebox.showwarning("경고", "초대할 사람을 선택하세요.")
            return

        # custom_room_name_entry에 입력한 값이 있다면 그 값을 사용하고, 없으면 기본 이름 생성
        custom_name = ""
        if hasattr(self, "custom_room_name_entry"):
            custom_name = self.custom_room_name_entry.get().strip()
            if custom_name == "단체방 이름을 입력하세요":
                custom_name = ""

        if custom_name:
            room_name = custom_name
        else:
            # 기본 이름 생성: 첫 번째 선택된 사원의 이름을 기준으로 (외 n명)
            first_member_code = selected_members[0]
            first_member_name = None
            for emp in employees_data:
                if emp.get("사원코드") == first_member_code:
                    first_member_name = emp.get("사원명")
                    break
            if first_member_name is None:
                first_member_name = first_member_code
            if len(selected_members) > 1:
                room_name = f"단체방: {first_member_name} (외 {len(selected_members) - 1}명)"
            else:
                room_name = f"단체방: {first_member_name}"

        # 채팅방 생성 요청 (예: 코드 85012)
        req = {
            "code": 85012,
            "args": {
                "room_name": room_name,
                "members": selected_members
            }
        }
        self.send_(json.dumps(req, ensure_ascii=False))
    def update_chatlist(self):
        for widget in self.fr_chatList.winfo_children():
            widget.destroy()

        # Treeview와 스크롤바를 담을 컨테이너 프레임 생성 (높이를 300픽셀로 고정)
        container = tk.Frame(self.fr_chatList, bg=Color.WHITE, height=300)
        container.pack(fill=tk.BOTH, expand=True)
        container.pack_propagate(False)

        # Treeview 생성
        tree = ttk.Treeview(container, columns=("room_id", "채팅방", "마지막 메시지"), show="headings")
        tree.heading("채팅방", text="채팅방")
        tree.heading("마지막 메시지", text="마지막 메시지")
        tree.column("room_id", width=0, stretch=False)
        tree.column("채팅방", width=150, anchor="center")
        tree.column("마지막 메시지", width=200, anchor="center")
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 수직 스크롤바 생성 및 연결
        scrollbar = tk.Scrollbar(container, orient="vertical", command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scrollbar.set)

        # chatrooms_data는 서버에서 받아온 채팅방 목록(각 요소가 딕셔너리)입니다.
        # 예를 들어, 각 방에 "members" 키가 있고, JSON 문자열 혹은 리스트 형태로 멤버 정보를 담고 있어야 합니다.
        data = chatrooms_data if chatrooms_data else []

        # 현재 사용자가 멤버로 포함된 채팅방만 필터링합니다.
        filtered_data = []
        for room in data:
            members = room.get("members")
            # 만약 members가 JSON 문자열이라면 파싱합니다.
            if isinstance(members, str):
                try:
                    members_list = json.loads(members)
                except Exception as e:
                    print("멤버 파싱 오류:", e)
                    members_list = []
            else:
                members_list = members
            # 현재 사용자의 id(self.root.id_)가 멤버 목록에 있다면 해당 방을 포함시킵니다.
            if self.root.id_ in members_list:
                filtered_data.append(room)

        # 필터링된 채팅방 목록을 Treeview에 추가합니다.
        for room in filtered_data:
            tree.insert("", tk.END, values=(room.get("room_id"), room.get("room_name"), room.get("last_message")))
        tree.bind("<Double-1>", lambda e: self.open_group_chat(tree))
    def open_group_chat(self, tree):
        selected = tree.selection()
        if selected:
            item = tree.item(selected[0], "values")
            room_id = item[0]
            room_name = item[1]
            req_join = {
                "code": 85015,
                "args": {
                    "room_id": int(room_id),
                    "employee_code": self.root.id_
                }
            }
            self.send_(json.dumps(req_join, ensure_ascii=False))
            self.show_chat(room_id, room_name)
    def update_chat(self):
        for widget in self.fr_chat.winfo_children():
            widget.destroy()
        self.fr_chat.grid_rowconfigure(0, weight=0)
        self.fr_chat.grid_rowconfigure(1, weight=1)
        self.fr_chat.grid_rowconfigure(2, weight=0)
        self.fr_chat.grid_columnconfigure(0, weight=1)

        # 상단에 채팅방 제목과 나가기 버튼을 추가
        header_frame = tk.Frame(self.fr_chat, bg=Color.WHITE)
        header_frame.grid(row=0, column=0, sticky="nsew", pady=5)
        lbl = tk.Label(header_frame, text=f"채팅: {self.current_chat_target}",
                       font=('맑은 고딕', 14, 'bold'), bg=Color.WHITE, fg=Color.BLACK)
        lbl.pack(side=tk.LEFT, padx=10)
        # 채팅방 나가기 버튼 추가 (버튼 클릭 시 leave_chat() 호출)
        btn_leave = tk.Button(header_frame, text="나가기", font=('맑은 고딕', 10),
                              bg=Color.BUTTON, fg=Color.WHITE, relief="flat",
                              activebackground=Color.FOCUS, command=self.leave_chat)
        btn_leave.pack(side=tk.RIGHT, padx=10)

        text_frame = tk.Frame(self.fr_chat, bg=Color.WHITE)
        text_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
        self.chat_history = tk.Text(text_frame, font=('맑은 고딕', 12),
                                    state="disabled", bg=Color.WHITE, fg=Color.BLACK, wrap="word")
        self.chat_history.grid(row=0, column=0, sticky="nsew")
        scrollbar = tk.Scrollbar(text_frame, command=self.chat_history.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.chat_history['yscrollcommand'] = scrollbar.set

        chat_input_frame = tk.Frame(self.fr_chat, bg=Color.WHITE, height=40)
        chat_input_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        chat_input_frame.grid_propagate(False)
        self.chat_input = tk.Entry(chat_input_frame, font=('맑은 고딕', 12), relief=tk.GROOVE, bd=2,
                                   bg=Color.WHITE, fg=Color.BLACK)
        self.chat_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.chat_input.bind("<Return>", self.sendMessage)
        send_btn = tk.Button(chat_input_frame, text="전송", font=('맑은 고딕', 12, 'bold'),
                             bg=Color.BUTTON, fg=Color.WHITE, relief="flat", activebackground=Color.FOCUS,
                             command=self.sendMessage)
        send_btn.pack(side=tk.RIGHT, padx=5)
    def sendMessage(self, event=None):
        message = self.chat_input.get().strip()
        if message:
            self.chat_input.delete(0, tk.END)
            # 기존: self.append_message("나", message)
            # 수정: 실제 이름으로 표시
            self.append_message(self.root.name, message)
            req = {
                "code": 75013,
                "args": {
                    "room_id": self.current_room_id,
                    "sender_id": self.root.id_,
                    "sender_name": self.root.name,
                    "message": message
                }
            }
            print("메세지 정보:", req)
            self.send_(json.dumps(req, ensure_ascii=False))
            self.chat_history.see("end")
            # self.load_chat_history()

        else:
            return
    def leave_chat(self):
        """
        현재 채팅방에서 나가기 요청을 서버에 전송.
        """
        # 현재 채팅방 정보와 현재 사용자의 id를 사용하여 leave_room 요청을 보냅니다.
        req = {
            "code": 85017,  # 채팅방 나가기 기능을 담당하는 코드 (서버의 f85017)
            "args": {
                "room_id": self.current_room_id,
                "employee_code": self.root.id_
            }
        }
        self.send_(json.dumps(req, ensure_ascii=False))
        # 나가기 요청 후, 채팅창을 초기화하거나 다른 화면(예: 채팅방 목록)으로 전환합니다.
        messagebox.showinfo("알림", "채팅방에서 나갔습니다.")
        # 예시: 채팅방 목록 화면으로 전환
        self.show_chatlist()
    def append_message(self, sender, message):
        self.chat_history.config(state="normal")
        self.chat_history.insert(tk.END, f"{sender}: {message}\n")
        self.chat_history.see("end")
        self.chat_history.config(state="disabled")
    def load_chat_history(self):
        """
        현재 채팅방의 이전 채팅 내역을 서버에 요청하는 함수입니다.
        f85016 코드를 사용하여 해당 room_id의 모든 메시지를 조회합니다.
        """
        req = {"code": 85016, "args": {"room_id": self.current_room_id}}
        self.send_(json.dumps(req, ensure_ascii=False))
    def send_(self, msg):
        try:
            # encoded = msg.encode()
            # test_socket.send(str(len(encoded)).ljust(16).encode())
            # test_socket.send(encoded)
            self.root.send_(msg)
        except Exception as e:
            print(traceback.format_exc())
            print(e)
    def recv(self, **kwargs):
        code = kwargs.get("code")
        sign = kwargs.get("sign")
        data = kwargs.get("data")
        # 채팅방 생성 관련 응답:
        if code == 85012:
            if sign == 1:
                messagebox.showinfo("채팅방 생성", "채팅방이 생성되었습니다.")
                req = {"code": 85014, "args": {}}
                self.send_(json.dumps(req, ensure_ascii=False))
            else:
                messagebox.showerror("채팅방 생성 실패", str(data))
        elif code == 85013:
            if sign == 1:
                print("code 85013 and sign 1")
                inner_data = data #data.get("data") if isinstance(data, dict) and "data" in data else data
                try:
                    received_room_id = int(inner_data.get("room_id"))
                except Exception as e:
                    print("room_id 변환 오류:", e)
                    return
                if received_room_id != self.current_room_id:
                    print("방이 다른듯", received_room_id, self.current_room_id)
                    return
                # 내 메시지는 이미 내 sendMessage()에서 추가했으므로 무시
                if inner_data.get("sender_id") == self.root.id_:
                    print("내꺼인듯")
                    return
                # 새 메시지를 즉시 추가하고 스크롤을 끝으로 이동
                self.append_message(inner_data.get("sender_name"), inner_data.get("message"))
                self.chat_history.see("end")
                # 전체 채팅  새로고침하고
                self.show_chat(self.current_room_id, self.current_chat_target)
            else:
                messagebox.showerror("채팅 전송 실패", str(data))

        # 채팅방 목록 조회 응답:
        elif code == 85014:
            if sign == 1 and data:
                global chatrooms_data
                chatrooms_data = data
                self.update_chatlist()
            else:
                messagebox.showinfo("알림", "채팅방 목록 조회 실패")
        # 직원 목록 조회 응답: (여기서는 기존 f85010 결과를 사용하는 것으로 남김)
        elif code == 85010:
            if sign == 1:
                global employees_data
                employees_data = data
                print("받은 직원 목록:", employees_data)
                self.update_main()
            else:
                messagebox.showinfo("알림", "직원 목록 조회 실패")
        elif code == 85016:
            if sign == 1:
                # data는 해당 채팅방의 메시지 목록 (딕셔너리 리스트)
                self.chat_history.config(state="normal")
                self.chat_history.delete("1.0", tk.END)
                for msg in data:
                    sender_name = msg.get("sender_name")
                    message = msg.get("message")
                    # 날짜와 시간은 표시하지 않습니다.
                    self.chat_history.insert(tk.END, f"{sender_name}: {message}\n")
                self.chat_history.config(state="disabled")
            else:
                messagebox.showinfo("알림", "채팅 내역 조회 실패")

def recv_thread_func(sock):
    def recv_all(count):
        buf = b""
        while count:
            newbuf = sock.recv(count)
            if not newbuf:
                return None
            buf += newbuf
            count -= len(newbuf)
        return buf

    while True:
        try:
            length_data = recv_all(16)
            if not length_data:
                break
            try:
                length = int(length_data.decode().strip())
            except Exception as e:
                print("길이 파싱 오류:", e)
                continue
            msg_data = recv_all(length)
            if not msg_data:
                continue
            decoded = msg_data.decode().strip()
            if decoded == "":
                continue
            try:
                msg_json = json.loads(decoded)
            except Exception as e:
                print(traceback.format_exc())
                continue
        except Exception as e:
            print("수신 스레드 오류:", e)
            break
