import os, sys, shutil
sys.path.append("source/")
import conf 

odir = 'output'

section_order = [
        'part',
        'chapter',
        'section',
        'subsection',
        'subsubsection',
        'paragraph',
        'subparagraph'
]

section_start = 2 # in case the doc class is article

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

    os.makedirs(odir,exist_ok=True)
    with open(f"{odir}/main.tex","w") as f:
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
                os.makedirs(f'{odir}/'+bib.split(bib.split('/')[-1])[0],exist_ok=True)
            shutil.copy('source/'+bib,'output/'+bib)
        f.write(r'''}'''+'\n')
        f.write(begindoc())
        f.write(r'''\tableofcontents'''+'\n')
        for doc in contents:
            f.write(r'''\input{'''+doc+r'''}'''+'\n')
        f.write(r'''\printbibliography'''+'\n')
        f.write(enddoc())

    isbib = False
    iscode = False
    isfig = False
    isenum = False
    label = ""
    for doc in contents:
        if len(doc.split('/'))>1:
            os.makedirs(f"{odir}/"+doc.replace(doc.split('/')[-1],""),exist_ok=True)
        with open(f'source/{doc}.rst') as f:
            lines = [l.split('\n')[0] for l in f.readlines()]
        ofile = open(f'{odir}/{doc}.tex','w')
        isLargeSect = 0
        for i, l in enumerate(lines):
            # sections 
            if i+1<len(lines):
                if (lines[i-1][:3]=="===") * (lines[i+1][:3]=="==="):
                    ofile.write(r'''\section{''' + l + r'''}''' + '\n')
                    isLargeSect = 1
                if lines[i+1][:3]=="===":
                    ofile.write("\\"+section_order[section_start+isLargeSect]+r'''{''' + l + r'''}''' + '\n')
                    continue
                elif lines[i+1][:3]=="---":
                    ofile.write("\\"+section_order[section_start+isLargeSect+1]+r'''{''' + l + r'''}''' + '\n')
                    continue
                elif lines[i+1][:3]=="^^^":
                    ofile.write("\\"+section_order[section_start+isLargeSect+2]+r'''{''' + l + r'''}''' + '\n')
                    continue
            if l[:3]=="===":
                continue
            if l[:3]=="---":
                continue
            if l[:3]=="^^^":
                continue
            # enumerate 
            if l[:2]=="#.":
                ltemp = ""
                if not isenum:
                    isenum = True
                    ltemp += r'''\begin{enumerate}''' + '\n'
                ltemp += r'''\item '''+l[3:]
                l = ltemp
            elif isenum:
                isenum = False
                l = r'''\end{enumerate}'''
            # bibtex
            if l[:3]=="   ":
                if isbib:
                    continue
            elif l[:6]==".. bib":
                isbib = True
                continue
            elif isbib:
                isbib = False
                continue
            # figure
            if l[:3]=="   ":
                if isfig:
                    if len(l)==3: 
                        continue
                    elif ":name:" in l:
                        label = r'''\label{'''+l.split(":name: ")[-1]+r'''}'''
                        continue
                    elif l[3]==":":
                        continue
                    else:
                        l = r'''\caption{'''+ l + r'''} ''' + label + '\n'
            elif l[:11]==".. figure::":
                isfig = True
                figfile = l[12:].split("*")[0] + "pdf"
                l = r'''\begin{figure}[htbp]'''+'\n' \
                    + r'''\centering''' + '\n' \
                    + r'''\includegraphics[width=.5\textwidth]{'''+figfile+r'''}'''
                os.makedirs(f'{odir}/'+figfile.split(figfile.split('/')[-1])[0],exist_ok=True)
                shutil.copyfile('source/'+figfile,f'{odir}/'+figfile)
            elif isfig:
                isfig = False
                l = r'''\end{figure}'''
                label = ""
            # toctree
            if l[:3]=="   ":
                if toctree:
                    if len(l)<4:
                        pass
                    elif l[3]==":":
                        continue
                    else:
                        contents.append(doc.replace(doc.split('/')[-1],'')+l[3:])
                        l = r'''\input{''' + contents[-1] + r'''}'''
            elif l[:10]==".. toctree":
                toctree = True
                continue
            elif toctree:
                toctree = False
                continue
            # code-block 
            if l[:3]=="   ":
                if iscode:
                    if len(l)<4:
                        continue
                    else:
                        l = l.replace("   ","")
            elif l[:13]==".. code-block":
                iscode = True
                l = r'''\begin{lstlisting}'''
            elif iscode:
                if lines[i-1][:13]==".. code-block":
                    continue
                else:
                    iscode = False
                    l = r'''\end{lstlisting}'''+'\n'
            # math mode 
            if ":math:" in l:
                p = l.split(r''':math:`''')
                l = p[0]
                for ii in range(len(p)):
                    if ii==0:
                        continue
                    l += r'''$'''
                    conv = False
                    for c in p[ii]:
                        if c==r'''`''':
                            if not conv:
                                c=r'''$'''
                                conv = True
                        l += c
            l = l.replace(r'''$\mathrm{\LaTeX}$''',r'''\LaTeX''')
            l = l.replace(r'''`\ ''',r'''}''')
            l = l.replace(r''' :cite:`''', r'''~\cite{''')
            l = l.replace(r''' ``''', r''' \texttt{''')
            l = l.replace(r''':numref:`fig:''',r'''Figure~\ref{fig:''')
            if l[:2]=="``":
                l = l[:2].replace("``",r'''\texttt{''')+l[2:]
            l = l.replace(r'''``''', r'''}''')
            ## find web link
            l = l.replace(r''' <htt''',r''' \href{htt''')
            websearch = l.split(r''' \href{htt''')
            if len(websearch)>1:
                for i in range(len(websearch)-1):
                    text = websearch[i].split(r''' `''')[-1]
                    l = l.replace(r''' `'''+text,'')
                    l = l.replace(r'''>`_\ ''',r'''}{'''+text+r'''}''')
                    l = l.replace(r'''>`_''',r'''}{'''+text+r'''}''')
            elif not (iscode + toctree + isbib):
                l = l.replace(r'''_''',r'''\_''')
            ofile.write(l + '\n')
        ofile.close()

    with open('typeset.sh','w') as tp:
        tp.write(r'''#!/bin/sh
cd '''+odir+r'''
cp main.tex temp.tex
platex temp
biber --debug temp
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
\documentclass[a4paper,11pt]{article}
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
\usepackage{listings,xcolor}
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

\lstset{basicstyle={\ttfamily\small},
        backgroundcolor={\color[gray]{.95}},
        numberstyle=\color{black}\ttfamily\footnotesize,
        breaklines=true
        }

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
