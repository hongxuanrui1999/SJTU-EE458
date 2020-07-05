from django import forms

#笔记名称,笔记内容,是否公开
class NoteForm(forms.Form):
    noteName = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'inputText', 'placeholder': '笔记名称'}))
    editordata = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'id': 'summernote', 'placeholder': 'Write Descriptions'}))
    '''
    note_ispublic = forms.BooleanField(
        widegt=forms.CheckboxInput()
    )
    '''