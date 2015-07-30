JekyllPost
====================

Sublime text 3插件,提高Sublime text下编写Jekyll Markdown文档,要求Python版本>3.0

功能
---
- 快速生成以'yyyy-mm-dd-'前缀的文档,并且根据文件名称自动生成文档头信息.
- 快速切换在发布箱与草稿箱之间
- 快速个性文档名称
- 快速删除不需要文档

默认快捷键(Mac)
---
- 创建 ``"super+j","super+n"``
- 名称修改 ``"super+j","super+r"``
- 删除 ``"super+j","super+d"``
- 转到草稿箱 ``"super+j","super+m"``
- 转到发布箱 ``"super+j","super+p"``

设置
---
- searchFolder : '_posts'目录,默认会自动搜索sublime text文件目录下的前上层
- fileExt : 文档扩展名,默认'.'
- drafts : '_drafts'目录,暂时只能与'_posts'同一层级
- template : 为创建文档时的头信息.
- categories : 根据文档名称映射分类名称,在头信息变量`${{categories}}`使用

其它
---
本人第一次写`sublime text`插件,也是第一次使用`python`.不好的地方就指点.
