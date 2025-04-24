#GUI Code:

import queue

def open_gui(cameras):
    gui = tk.Tk()
    gui.title("Watchful Webcams Panel")

    log_view = scrolledtext.ScrolledText(gui, width = 80, height = 20)      #Set log box size in GUI
    log_view.pack(padx = 10, pady = 10)
    #Log Buttons
    refresh_btn = tk.Button(gui, text="Refresh Log", command=lambda: load_log(log_view))
    refresh_btn.pack(pady=5)
    clear_btn = tk.Button(gui, text="Clear Log", command=lambda: clear_log(log_view))
    clear_btn.pack(pady=5)
    #Camera Buttons
    btn_frame = tk.Frame(gui)
    btn_frame.pack(pady = 10)
    for cam in cameras:
        tk.Button(
                btn_frame,
                text=f"{cam.name}",
                command=lambda c=cam: open_camera_window(c, gui)
            ).pack(side=tk.LEFT, padx=5)
    load_log(log_view)
    gui.mainloop()

def load_log(widget):
    try:
        with open("activity_log.txt", "r") as f:
            widget.delete(1.0, tk.END)
            widget.insert(tk.END, f.read())
    except FileNotFoundError:
        widget.delete(1.0, tk.END)
        widget.insert(tk.END, "No log found. \n")

def clear_log(widget):
    wipe_log()
    widget.delete(1.0, tk.END)
    widget.insert(tk.END, "LOG CLEARED.\n")

def open_camera_window(camera, parent):
    global pause_polling
    if pause_polling:
        return
    pause_polling = True
    top = Toplevel(parent)
    top.title(f"Live: {camera.name}")
    waiting_lbl = Label(top, text=f"waiting for camera to become avaliable...")
    waiting_lbl.pack()

    stop = threading.Event()

    def on_close():
        stop.set()
        #Do not try to release a camera that never successfully opened
        if 'cap' in locals() and cap is not None:
            cap.release()
        top.destroy()
        global pause_polling
        pause_polling = False
    top.protocol("WM_DELETE_WINDOW", on_close)

    cap = None
    while not stop.is_set():        #Try and open the camera (it may be being polled currently)
        cap = safe_open_cam(camera.source)
        if cap:
            break
        time.sleep(0.1)

    if stop.is_set() or cap is None:    #bail if user closes window
        return
    waiting_lbl.destroy()
    lbl = Label(top)
    lbl.pack()

    if cap is None:
        write_log_entry(f"Failed to open camera {camera.source}")
        on_close()
        return

    window_start = time.time()
    warmup_duration = 2.0
    def update_frame():
        if stop.is_set():
            return
        ret, frame = cap.read()
        if ret and frame is not None:
            if time.time() - window_start < warmup_duration:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = ImageTk.PhotoImage(Image.fromarray(rgb))
                lbl.imgtk = img
                lbl.config(image=img)
                lbl.after(30, update_frame)
                return

            height, width = frame.shape[:2]
            # Create blob and forward pass
            blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
            net.setInput(blob)
            outputs = net.forward(net.getUnconnectedOutLayersNames())

            boxes, confidences = [], []
            for output in outputs:
                for detection in output:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = float(scores[class_id])
                    if class_id == 0 and confidence > 0.5:
                        if not (math.isfinite(detection[2]) and math.isfinite(detection[3])):
                            continue
                        w_rel, h_rel = detection[2], detection[3]
                        if w_rel <= 0 or h_rel <= 0 or w_rel > 1 or h_rel > 1:
                            continue
                        cx, cy = detection[0] * width, detection[1] * height
                        w, h = int(w_rel * width), int(h_rel * height)
                        x, y = int(cx - w / 2), int(cy - h / 2)
                        x, y = max(0, x), max(0, y)
                        w = min(w, width - x)
                        h = min(h, height - y)
                        boxes.append([x, y, w, h])
                        confidences.append(confidence)

            indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
            if len(indices) > 0:
                idx_list = indices.flatten() if hasattr(indices, 'flatten') else indices
                first_idx = idx_list[0]
                x, y, w, h = boxes[first_idx]
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f"Person: {confidences[first_idx]:.2f}", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)


            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = ImageTk.PhotoImage(Image.fromarray(rgb))
            lbl.imgtk = img
            lbl.config(image=img)
        # schedule next frame
        lbl.after(30, update_frame)

    update_frame()
