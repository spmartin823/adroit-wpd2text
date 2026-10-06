# adroit-wpd2text

Small Python wrapper for `wpd2text`, the WordPerfect text converter from
[libwpd](https://libwpd.sourceforge.net/). This is an unofficial distribution,
not affiliated with the libwpd project or Corel.

```python
from adroit_wpd2text import extract_text

text = extract_text(wordperfect_file_bytes)
```

The wheels bundle `wpd2text` and its libwpd/librevenge dependencies. Linux
wheels use the Amazon Linux 2023 packages (libwpd 0.10.3, librevenge 0.0.4).
macOS wheels use the Homebrew packages (libwpd 0.10.3, librevenge 0.0.6).
The upstream source releases are available from the
[libwpd project](https://sourceforge.net/projects/libwpd/files/libwpd/libwpd-0.10.3/)
and [librevenge project](https://sourceforge.net/projects/libwpd/files/librevenge/).
The license texts are included in each wheel.
