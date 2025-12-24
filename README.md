# mkdocs-material-equation-plugin
A plugin that allows you to preview equations with mkdocs-material.

## Install

Download with git and install with pip

```bash
  git clone https://github.com/PhysCourse/mkdocs-material-equation-plugin.git
  cd mkdocs-material-equation-plugin
  pip install .
```

## Usage

in markdown equations like 

```markdown
\begin{equation}
  \label{eq:myeq}
  \int_a^b{f(x)dx} = F(b)-F(a)
\end{equation}
```

could be referenced as ```[ref text](#eq:myeq)```

