from mongoengine import StringField, IntField,Document, EmbeddedDocument,ListField, EmbeddedDocumentField

class Data(EmbeddedDocument):
    offence = StringField(required=True, max_length=200)
    type = StringField(required=True, max_length=200)
    data1 = StringField(required=True,max_length=50)
    data2 = StringField(required=True,max_length=50)
    data3 = StringField(required=True,max_length=50)
    data4 = StringField(required=True,max_length=50)
    data5 = StringField(required=True,max_length=50)
    data6 = StringField(required=True,max_length=50)
    data7 = StringField(required=True,max_length=50)
    data8 = StringField(required=True,max_length=50)
    data9 = StringField(required=True,max_length=50)
    data10 = StringField(required=True,max_length=50)
    data11 = StringField(required=True,max_length=50)
    data12 = StringField(required=True,max_length=50)
    data13 = StringField(required=True,max_length=50)


  #  type = StringField(required=True, max_length=50)

    def __init__(self, offence, type,data1,data2,data3,data4,data5,data6,data7,data8,data9,data10,data11,data12,data13, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.offence = offence
        self.type = type
        self.data1 = data1
        self.data2 = data2
        self.data3 = data3
        self.data4 = data4
        self.data5 = data5
        self.data6 = data6
        self.data7 = data7
        self.data8 = data8
        self.data9 = data9
        self.data10 = data10
        self.data11 = data11
        self.data12 = data12
        self.data13 = data13

class Offence(Document):
    id = StringField(required=True, primary_key=True)
    region = StringField(required=True, max_length=50)
    data = ListField(EmbeddedDocumentField(Data))

    def __init__(self, id,region, data=[], *args, **values):
        super().__init__(*args, **values)
        self.id = id
        self.region = region
        self.data = data

