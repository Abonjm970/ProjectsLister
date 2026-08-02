# ProjectsLister (projls)

[English](#english) | [العربية](#العربية)

---

<a id="english"></a>
## English

**ProjectsLister** (or `projls`) is a fast, keyboard-driven Terminal User Interface (TUI) tool designed to help you quickly navigate between your most frequently used project directories from the command line.

### Why ProjectsLister?
- **Speed:** Quickly jump to projects without typing long `cd` paths.
- **Efficient:** Full keyboard control (no mouse needed).
- **Smart:** Automatically orders projects by "Most Recently Used" (MRU).
- **Integrated:** The `projls` command seamlessly changes your current terminal directory.

### Installation

#### Prerequisites
- Python 3.10+
- `pipx` (Recommended for global tool installation)

#### Steps

1. **Install the package:**
   ```bash
   pipx install projectslister
   ```

2. **Enable Shell Integration:**
   Run the following command once to add the `projls` function to your shell profile (`~/.bashrc` or PowerShell profile):
   ```bash
   projectslister --install-shell
   ```
   *Note: Open a new terminal window or run `source ~/.bashrc` (on Linux/macOS) / `& $PROFILE` (on Windows) to activate the command.*

### Usage

Simply type `projls` in your terminal to open the TUI:

```bash
projls
```

#### Keyboard Shortcuts
| Key | Action |
| :--- | :--- |
| `a` | Add a new project |
| `e` | Edit the selected project |
| `d` | Delete the selected project |
| `/` | Search projects |
| `Enter` | Open (navigate to) the selected project |
| `Esc` | Go back / Cancel |
| `q` | Quit |

### How it works
ProjectsLister saves you from manual path management. When you select a project in the TUI, it exits and prints the path, which is then captured by the `projls` shell function to execute the `cd` command in your current terminal session.

---

<a id="العربية"></a>
## العربية

**ProjectsLister** (أو `projls`) هو برنامج واجهة طرفية تفاعلي (TUI) مُصمم لتسريع التنقل بين مجلدات مشاريعك الأكثر استخداماً عبر سطر الأوامر.

### لماذا ProjectsLister؟
- **السرعة:** انتقل إلى مشاريعك بضغطة زر دون الحاجة لكتابة مسارات `cd` الطويلة.
- **الكفاءة:** تحكم كامل عبر لوحة المفاتيح (لا حاجة للفأرة).
- **الذكاء:** ترتيب تلقائي للمشاريع حسب الأكثر استخداماً مؤخراً (MRU).
- **التكامل:** أمر `projls` يقوم بتغيير المجلد الحالي في طرفيتك تلقائياً عند اختيار المشروع.

### التثبيت

#### المتطلبات
- Python 3.10+
- `pipx` (يُوصى به لتثبيت البرامج عالمياً)

#### الخطوات

1. **تثبيت الحزمة:**
   ```bash
   pipx install projectslister
   ```

2. **تفعيل التكامل مع الطرفية:**
   قم بتشغيل الأمر التالي لمرة واحدة لإضافة دالة `projls` إلى ملف تهيئة الطرفية (`~/.bashrc` أو ملف `Profile` الخاص بـ PowerShell):
   ```bash
   projectslister --install-shell
   ```
   *ملاحظة: افتح نافذة طرفية جديدة أو قم بتنفيذ `source ~/.bashrc` (على Linux/macOS) / `& $PROFILE` (على Windows) لتفعيل الأمر.*

### الاستخدام

اكتب ببساطة `projls` في الطرفية لفتح الواجهة التفاعلية:

```bash
projls
```

#### اختصارات لوحة المفاتيح
| المفتاح | الوظيفة |
| :--- | :--- |
| `a` | إضافة مشروع جديد |
| `e` | تعديل المشروع المحدد |
| `d` | حذف المشروع المحدد |
| `/` | البحث في المشاريع |
| `Enter` | فتح (الانتقال إلى) المشروع المحدد |
| `Esc` | رجوع / إلغاء |
| `q` | خروج |

### كيف يعمل؟
يوفر عليك ProjectsLister عناء إدارة المسارات يدوياً. عند اختيارك لمشروع داخل الواجهة، يقوم البرنامج بإغلاق نفسه وطباعة مسار المجلد، والذي تلتقطه دالة `projls` في الطرفية لتنفيذ أمر `cd` ونقلك مباشرة إلى المجلد.
