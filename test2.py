str = "    invoke-virtual {v0}, Landroid/content/Intent;->getExtras()Landroid/os/Bundle;"
content = ['.method public R0()Ljava/lang/String;', 
'    .registers 2',
'',
'    .line 1',
'    iget-object v0, p0, Lim/xingzhe/chat/ui/ChatActivity;->k:Ljava/lang/String;',
'',
'    return-object v0'
'.end method']

first_str = ""
for word in content:
    for s in word.split(' '):
        # print(s)
        if s:
            first_str = s
            break
    print(first_str)