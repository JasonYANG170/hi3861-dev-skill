# LiteOS-M kernel development

Use the API family already present in the selected Vendor example. PZ examples `01_os_task` through `07_os_timer` demonstrate tasks, queues, binary/counting semaphores, mutexes, events, and software timers against this SDK.

## Routes

- Task creation, priority, stack, delay, and deletion: `hi_task.h` and `kernel/liteos_m/kernel/base/core/los_task.c`.
- Message queues: `hi_msg.h`, LiteOS queue headers/implementation, PZ `02_os_queue`.
- Semaphores and mutexes: `hi_sem.h`, `hi_mux.h`, PZ `03`-`05` examples.
- Events: `hi_event.h`, LiteOS event implementation, PZ `06_os_event`.
- Software/hardware timers and time conversion: `hi_timer.h`, `hi_hrtimer.h`, `hi_time.h`, PZ `07_os_timer` and `15_time`.
- Memory, ISR, work queues, and diagnostics: `hi_mem.h`, `hi_isr.h`, `hi_workqueue.h`, kernel source, and SDK-native demos.

Always verify stack sizes, priority direction, timeout units, ISR-call restrictions, and object lifetime in the actual header/source. Ensure callbacks do not block where the SDK executes them in interrupt or timer context.
