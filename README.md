# FileTransferProgram
<!DOCTYPE HTML>
<html>
<body>
<p>I have written two scripts in python. One is to send files and directories and the other to receive</p>
<h2>Installation</h2>
<p>git clone https://github.com/Hasham14/FileTransferProgram.git</p>
<p>cd FlieTransferProgram</p>
<p>chmod +x *</p>
<h2>Usage</h2>
<h4>To Send Files and Directories</h4>
<p>./sender.py [options] {file1} {file2} {file3...}</p>
<h4>To Receive Files and Directories</h4>
<p>./receiver.py [options] {host} {port}</p>
<h2>Requirements</h2>
<p>Requires the latest version of python or at least version 3.8</p>
<p>If any module is missing just type pip install {module name} and install it</p>
<h2>TODO</h2>
<ul>
<li><p>Add support for DNS</p>
<li><p>Add encryption to prevent MITM attacks</p>
<li><p>Send and receive files and directories simaltaneously from multiple sender and receivers</p>
</ul>
</body>
</html>
