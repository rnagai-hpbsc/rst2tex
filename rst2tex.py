import os, sys, shutil
sys.path.append("source/")
import conf 

def main():
    with open('source/index.rst') as f:
        index = [l.split('\n')[0] for l in f.readlines()]
    
    cmtout = False
    titlef = False
    toctree = False
    contents = []
    title = ""
    for i, l in enumerate(index):
        #print(l)
        if i==0: 
            cmtout = True
            continue
        if l[:3]=="   ":
            if cmtout:
                continue
            elif toctree:
                if len(l)<4:
                    pass
                elif l[3]==":":
                    continue
                else:
                    contents.append(l[3:])
        elif cmtout:
            cmtout = False
        elif l[:3]=="===":
            continue
        elif l[:10]==".. toctree":
            toctree = True
        elif toctree:
            toctree = False
        elif i+1<len(index):
            if index[i+1][:3]=="===":
                title = r'''\title{''' + l + r'''}'''
            else:
                #print(l)
                pass

    with open("rst2tex/output/main.tex","w") as f:
        f.write(preamble())
        f.write(title+'\n')
        f.write(r'''\author{'''+conf.author+r'''}'''+'\n')
        # add bib
        f.write(r'''\addbibresource{''')
        for i, bib in enumerate(conf.bibtex_bibfiles):
            if i>0:
                f.write(r''',''')
            f.write(bib)
            if len(bib.split('/'))>1:
                os.makedirs('rst2tex/output/'+bib.split(bib.split('/')[-1])[0],exist_ok=True)
            shutil.copy('source/'+bib,'rst2tex/output/'+bib)
        f.write(r'''}'''+'\n')
        f.write(begindoc())
        f.write(r'''\tableofcontents'''+'\n')
        for doc in contents:
            f.write(r'''\input{'''+doc+r'''}'''+'\n')
        f.write(r'''\printbibliography''')
        f.write(enddoc())

    isbib = False
    for doc in contents:
        if len(doc.split('/'))>1:
            os.makedirs(doc.replace('rst2tex/output/'+doc.split('/')[-1]),exist_ok=True)
        with open(f'source/{doc}.rst') as f:
            lines = [l.split('\n')[0] for l in f.readlines()]
        ofile = open(f'rst2tex/output/{doc}.tex','w')
        for i, l in enumerate(lines):
            if i+1<len(lines):
                if lines[i+1][:3]=="===":
                    ofile.write(r'''\section{'''+ l + r'''}'''+'\n')
                    continue
            if l[:3]=="===":
                continue
            if l[:6]==".. bib":
                isbib = True
                continue
            if l[:3]=="   ":
                if isbib:
                    continue
            else:
                if isbib:
                    isbib = False
            l = l.replace(r'''`\ ''',r'''}''')
            l = l.replace(r''' :cite:`''', r'''~\cite{''')
            l = l.replace(r''' ``''', r''' \texttt{''')
            l = l.replace(r'''`` ''', r'''} ''')
            ## find web link
            l = l.replace(r''' <htt''',r''' \href{htt''')
            websearch = l.split(r''' \href{htt''')
            if len(websearch)>1:
                for i in range(len(websearch)-1):
                    text = websearch[i].split(r''' `''')[-1]
                    l = l.replace(r''' `'''+text,'')
                    l = l.replace(r'''>`_\ ''',r'''}{'''+text+r'''}''')
                    l = l.replace(r'''>`_''',r'''}{'''+text+r'''}''')
            ofile.write(l + '\n')
        ofile.close()

    with open('typeset.sh','w') as tp:
        tp.write(r'''#!/bin/sh
cd rst2tex/output
cp main.tex temp.tex
platex temp
biber temp
platex temp
platex temp
dvipdfmx -o main.pdf temp
rm temp*
cd -
''')
        
    os.system('. ./typeset.sh')
    os.remove('typeset.sh')

    return

def preamble():
    text = r'''
\documentclass[a4paper,12pt]{article}
\usepackage[margin=2.5cm]{geometry}
\usepackage{amsmath,amssymb}
\usepackage[dvipdfmx,dvips]{graphicx}
\usepackage[dvipdfmx]{color}
\usepackage[dvipdfmx,
            bookmarkstype=toc=true,
            colorlinks=true,
            linkcolor=blue,
            urlcolor=magenta,
            citecolor=red,
            bookmarksnumbered=true,
            bookmarks=true]{hyperref}
\usepackage{pxjahyper}
\usepackage{lscape}
\usepackage{booktabs}
\usepackage{enumitem}
\usepackage{mathptmx}
\usepackage[small]{caption}
\usepackage{physics}
\usepackage{siunitx}

\usepackage[style=phys,
            biblabel=brackets,
            chaptertitle=false,
            eprint=true,
            pageranges=false,
            defernumbers,
            backend=biber]
            {biblatex}
\renewbibmacro{in:}{}
\DeclareFieldFormat*{title}{\textit{``#1``}}
\DeclareFieldFormat*{citetitle}{\textit{``#1``}}
'''
    return text

def begindoc():
    return r'''
\begin{document}
\maketitle
'''

def enddoc():
    return r'''\end{document}'''

if __name__=='__main__':
    main()
