import json
import tkinter as tk
import tkinter.ttk as ttk
from keyword import kwlist
import tablewidget
import pymysql
import tkinter.messagebox as msgbox


class plantFrame(tk.Frame):
    def __init__(self, root):
        super().__init__(root, width=1300, height=700)
        self.root = root

        self.fr_right = tk.Frame(self, width=350, height=350)  # 오른쪽 구역
        self.fr_left = tk.Frame(self, width=950, height=350)  # 왼쪽구역
        self.fr_buttom = tk.Frame(self, width=1300, height=350)  # 아래테이블구역

        self.fr_left.grid(row=0, column=0)
        self.fr_right.grid(row=0, column=1)
        self.fr_buttom.grid(row=1, column=0, columnspan=2)

        self.fr_left.grid_propagate(False)
        self.fr_left.pack_propagate(False)
        self.fr_right.grid_propagate(False)
        self.fr_right.pack_propagate(False)
        self.fr_buttom.grid_propagate(False)
        self.fr_buttom.pack_propagate(False)

        self.la_select = tk.Label(self.fr_right, text="조회 필드값", font=('Arial', 10, "bold"))
        self.la_select.place(x=90, y=15)

        self.la_plantName = tk.Label(self.fr_right, text="창고명")
        self.la_plantName.place(x=15, y=45)
        self.en_plantName = tk.Entry(self.fr_right)
        self.en_plantName.place(x=70, y=45)

        self.la_plantCode = tk.Label(self.fr_right, text="창고코드")
        self.la_plantCode.place(x=15, y=75)
        self.en_plantCode = tk.Entry(self.fr_right)
        self.en_plantCode.place(x=70, y=75)

        self.la_plantLocation = tk.Label(self.fr_right, text="창고위치")
        self.la_plantLocation.place(x=15, y=105)
        self.en_plantLocation = tk.Entry(self.fr_right)
        self.en_plantLocation.place(x=70, y=105)

        self.bt_read = tk.Button(self.fr_right, text="조회", width=7, command=self.Psearch)
        self.bt_read.place(x=250, y=40)

        self.bt_modify = tk.Button(self.fr_right, text="수정", width=7, command=self.modify)
        self.bt_modify.place(x=250, y=80)

        self.bt_save = tk.Button(self.fr_right, text="저장", width=7, command=self.save)
        self.bt_save.place(x=250, y=120)

        self.bt_create = tk.Button(self.fr_right, text="등록", width=7, command=self.Rwindow)
        self.bt_create.place(x=250, y=160)

        self.la_materialCode = tk.Label(self.fr_left, text="자재코드")
        self.la_materialCode.place(x=100, y=15)
        self.en_materialCodeL = tk.Entry(self.fr_left)
        self.en_materialCodeL.place(x=170, y=15)
        self.en_materialCodeL.config(state="disabled")

        self.la_materialName = tk.Label(self.fr_left, text="자재명")
        self.la_materialName.place(x=100, y=53)
        self.en_materialNameL = tk.Entry(self.fr_left)  # 자재명 엔트리 박스
        self.en_materialNameL.place(x=170, y=53)  # 자재명 엔트리박스 배치
        self.en_materialNameL.config(state="disabled")

        self.la_materialType = tk.Label(self.fr_left, text="자재유형")
        self.la_materialType.place(x=100, y=93)
        self.en_materialType = tk.Entry(self.fr_left)  # 자재명 엔트리 박스
        self.en_materialType.place(x=170, y=93)  # 자재명 엔트리박스 배치
        self.en_materialType.config(state="disabled")

        self.la_plantNameL = tk.Label(self.fr_left, text="창고명")
        self.la_plantNameL.place(x=100, y=133)
        self.en_plantNameL = tk.Entry(self.fr_left)  # 자재명 엔트리 박스
        self.en_plantNameL.place(x=170, y=133)  # 자재명 엔트리박스 배치
        self.en_plantNameL.config(state="disabled")

        self.la_plantCodeL = tk.Label(self.fr_left, text="창고코드")
        self.la_plantCodeL.place(x=100, y=173)
        self.en_plantCodeL = tk.Entry(self.fr_left)
        self.en_plantCodeL.place(x=170, y=173)
        self.en_plantCodeL.config(state="disabled")

        self.la_plantLocationL = tk.Label(self.fr_left, text="창고위치")
        self.la_plantLocationL.place(x=100, y=213)
        self.en_plantLocationL = tk.Entry(self.fr_left)
        self.en_plantLocationL.place(x=170, y=213)
        self.en_plantLocationL.config(state="disabled")

        self.la_rec_quantity = tk.Label(self.fr_left, text="입고수량")
        self.la_rec_quantity.place(x=600, y=15)
        self.en_rec_quantity = tk.Entry(self.fr_left)
        self.en_rec_quantity.place(x=680, y=15)
        self.en_rec_quantity.config(state="disabled")

        self.la_price = tk.Label(self.fr_left, text="단가")
        self.la_price.place(x=600, y=53)
        self.en_price = tk.Entry(self.fr_left)
        self.en_price.place(x=680, y=53)
        self.en_price.config(state="disabled")

        self.la_unit = tk.Label(self.fr_left, text="단위")
        self.la_unit.place(x=600, y=93)
        self.en_unit = tk.Entry(self.fr_left, width=17)
        self.en_unit.place(x=680, y=93)
        self.en_unit.config(state="disabled")



        self.check = ''

        self.data = None  #일단 테이블 생성자 만들어놓음
        self.app1 = tablewidget.TableWidget(self.fr_buttom,
                                            data=self.data,
                                            col_name=["자재코드", "자재명", "자재유형", "창고명", "창고코드", "창고위치", "창고총수량", "단가", "단위"],
                                            col_width=[100, 200, 200, 130, 130, 130, 130, 100, 110],
                                            width=1300,
                                            height=200)
        self.app1.grid(row=1, column=0, columnspan=2)
        self.bind("<F5>", lambda e: test())

        def test():
            print(f"data: {self.app1.data}")  # 저장된 데이터
            print(f"rows cols: {self.app1.rows} {self.app1.cols}")  # 행 열 개수
            print(f"selected: {self.app1.selected_row} {self.app1.selected_col}")  # 선택된 행 열 index
            print(f"changed {self.app1.changed}")  # 원본 대비 변경된 데이터

    def after_init(self): #생성 후 호출함수
        self.Psearch() # 조회함수 호출해서 테이블 만들어지게

    def save(self):  # 저장버튼 누르면 실행되는 함수, 얘는

        d = {
            "check": self.check,
            "material_code": self.en_materialCodeL.get(),
            "material_name": self.en_materialNameL.get(),
            "material_type": self.en_materialType.get(),
            "plant_name": self.en_plantNameL.get(),
            "plant_code": self.en_plantCodeL.get(),
            "plant_location": self.en_plantLocationL.get(),
            "quantity": self.en_rec_quantity.get(),
            "price": self.en_price.get(),
            "unit": self.en_unit.get().strip()
        }

        send_d = {
            "code": 20608,
            "args": d
        }
        self.root.send_(json.dumps(send_d, ensure_ascii=False))

    def modify(self):
        self.check = 'M'
        selected_index = self.app1.selected_row  # selected_row가 선택된 행
        if selected_index is None:
            return
        selected_data = self.app1.data[selected_index]  # 선택된 행의 데이터 가져오기
        if not selected_data:
            return
        selected_values = selected_data.get("data", [])
        if not isinstance(selected_values, list):
            return
        entries = [
            (self.en_materialCodeL, "자재코드", 0),
            (self.en_materialNameL, "자재명", 1),
            (self.en_materialType, "자재유형", 2),
            (self.en_plantNameL, "창고명", 3),
            (self.en_plantCodeL, "창고코드", 4),
            (self.en_plantLocationL, "창고위치", 5),
            (self.en_rec_quantity, "입고수량", 6),
            (self.en_price, "단가", 7),
            (self.en_unit, "단위", 8)
        ]

        for entry, key, index in entries:
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, selected_values[index] if index < len(selected_values) and selected_values[
                index] is not None else "")
        msgbox.showinfo("완료", "선택되었습니다")


    def Rwindow(self):  # 등록 버튼 누르면 새창 나오는 함수
        self.check = 'C'
        self.newWindow = tk.Toplevel(self)
        self.newWindow.geometry("800x400")
        self.newWindow.title("입고 기록 조회")

        # 라벨 추가
        la_receiving = tk.Button(self.newWindow, text="입고기록조회", font=("Arial", 14), command=self.Rsearch)
        la_receiving.place(x=300, y=10)

        bt_select = tk.Button(self.newWindow, text="선택", command=self.Rselec)
        bt_select.place(x=760, y=50)

    def Rselec(self):  # 입고로그셀렉하기
        selected_index = self.app2.selected_row  # 선택된 행의 인덱스 가져오기
        if selected_index is None:
            return
        selected_data = self.app2.data[selected_index]  # 선택된 행의 데이터 가져오기
        if not selected_data:
            return
        selected_values = selected_data.get("data", [])
        if not isinstance(selected_values, list):
            return
        entries = [
            (self.en_materialCodeL, "자재코드", 0),
            (self.en_materialNameL, "자재명", 1),
            (self.en_materialType, "자재유형", 2),
            (self.en_plantNameL, "창고명", 3),
            (self.en_plantCodeL, "창고코드", 4),
            (self.en_plantLocationL, "창고위치", 5),
            (self.en_rec_quantity, "입고수량", 6),
            (self.en_price, "단가", 7),
            (self.en_unit, "단위", 8)
        ]

        for entry, key, index in entries:
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, selected_values[index] if index < len(selected_values) and selected_values[
                index] is not None else "")

        msgbox.showinfo("완료", "선택되었습니다")
        self.newWindow.destroy()
        print(f" selected_values: {selected_values}")

    def Rsearch(self):  # 입고기록조회
        send_d = {
            "code": 20606,
            "args": {}
        }
        self.root.send_(json.dumps(send_d, ensure_ascii=False))

    def Psearch(self):  # 창고자재 조회
        keys = ["plant_code", "plant_name", "plant_location"]
        values = [self.en_plantCode.get(), self.en_plantName.get(), self.en_plantLocation.get()]

        d = {k: v for k, v in zip(keys, values) if v}  # 값이 있는 경우에만 dict에 추가

        send_d = {
            "code": 20605,
            "args": d
        }

        self.root.send_(json.dumps(send_d, ensure_ascii=False))

    # @staticmethod
    # @MsgProcessor
    # def f20605(**kwargs):  # 창고 기록 조회
    #     base_query = "SELECT material_code, material_name, material_type, plant_name, plant_code, plant_location, quantity, price, unit FROM plant_material"
    #     conditions = []
    #     params = []
    #     for key, value in kwargs.items():
    #         if value:  # 값이 비어 있지 않은 경우에만 조건 추가
    #             conditions.append(f"{key} LIKE %s")
    #             params.append(f"%{value}%")
    #
    #     if conditions:
    #         query = f"{base_query} WHERE {' AND '.join(conditions)}"
    #     else:
    #         query = base_query  # 조건이 없으면 전체 조회
    #
    #     print(f"SQL Query: {query}, Params: {params}")
    #     result = dbm.query(query, params)
    #
    #     if result:
    #         material_data = [list(row) for row in result]  # 검색된 데이터를 리스트로 변환
    #         return {'sign': 1, "data": material_data}
    #     else:
    #         return {'sign': 0, "data": []}
    #
    # @staticmethod
    # @MsgProcessor
    # def f20606(**kwargs):  # 입고기록 조회일경우
    #     query = """
    #                               SELECT receiving.material_code, receiving.material_name, receiving.receiving_classification,
    #                                      plant.plant_name, plant.plant_code, plant.location,
    #                                      receiving.quantity,receiving.price, receiving.unit
    #                               FROM receiving
    #                               JOIN plant ON receiving.plant_code = plant.plant_code
    #                           """
    #     result = dbm.query(query, [])  # 만약 성공이면 데이터가 아니면 None이 result에 들어옴
    #     print("result", result)
    #     if result is not None:
    #         material_data = [list(row) for row in result]  # 성공했으면 result를 리스트 형태로 변화
    #         return {'sign': 1, "data": material_data}
    #     else:
    #         return {'sign': 0, "data": []}
    #
    #
    # @staticmethod
    # @MsgProcessor
    # def f20608(**kwargs):
    #     if kwargs.get("check") == 'M':
    #         query = """
    #                      UPDATE erp_db.plant_material
    #                      SET material_name = %s, material_type = %s, plant_name = %s, plant_code = %s,
    #                          plant_location = %s, quantity = %s, price = %s, unit = %s
    #                      WHERE material_code = %s
    #                  """
    #         params = [
    #             kwargs.get("material_name"), kwargs.get("material_type"),
    #             kwargs.get("plant_name"), kwargs.get("plant_code"),
    #             kwargs.get("plant_location"), kwargs.get("quantity"),
    #             int(kwargs.get("price")),
    #             kwargs.get("unit"),
    #             kwargs.get("material_code"),
    #         ]
    #         print(f"🛠 UPDATE params 확인: {params}")
    #
    #         result = dbm.query(query, tuple(params))
    #
    #         if result is not None:
    #             return {'sign': 1, "data": []}
    #         else:
    #             return {'sign': 0, "data": []}
    #
    #     if kwargs.get("check") == 'C':
    #         query = """
    #                      INSERT INTO erp_db.plant_material (material_code, material_name, material_type, plant_name, plant_code,
    #                          plant_location, quantity, price, unit)
    #                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    #                  """
    #         params = [
    #             kwargs.get("material_code"), kwargs.get("material_name"), kwargs.get("material_type"),
    #             kwargs.get("plant_name"), kwargs.get("plant_code"),
    #             kwargs.get("plant_location"), kwargs.get("quantity"),
    #             int(kwargs.get("price")),
    #             kwargs.get("unit"),
    #         ]
    #         print(f"🛠 INSERT params 확인: {params}")
    #
    #         result = dbm.query(query, tuple(params))
    #
    #         if result is not None:
    #             return {'sign': 1, "data": []}
    #         else:
    #             return {'sign': 0, "data": []}

    def recv(self, **kwargs):  # 서버로부터 받은 데이터 처리
        print("code:", kwargs.get("code"))
        print("sign:", kwargs.get("sign"))
        print("data:", kwargs.get("data"))

        if kwargs.get("sign") == 1:
            if kwargs.get("code") == 20605:  # 창고자재 조회일 경우
                self.data = kwargs.get("data")
                self.app1.refresh(self.data)  # 테이블 갱신

            elif kwargs.get("code") == 20606:  # 입고기록 조회일 경우
                self.data = kwargs.get("data")
                self.app2 = tablewidget.TableWidget(
                    self.newWindow,
                    data=self.data,
                    col_name=["자재코드", "자재명", "자재유형", "창고명", "창고코드", "창고위치", "창고총수량", "단가", "단위"],
                    col_width=[100, 100, 100, 100, 100, 100, 100, 50, 50],
                    width=800,
                    height=200
                )
                self.app2.place(x=0, y=100)


            elif kwargs.get("code") == 20608:  # 저장 후 다시 조회
                self.Psearch()
        else:
            if kwargs.get("code") == 20608:
                msgbox.showinfo("저장불가", "입력 형식이 올바르지 않습니다.")




# 테스트용 코드
if __name__ == "__main__":
    r = tk.Tk()
    r.geometry("1600x900")
    r.config(bg="white")
    fr = plantFrame(r)
    fr.place(x=300, y=130)
    r.mainloop()