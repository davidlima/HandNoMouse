log_={}
log_text__=""
def init():
    global log_,log_text__
    log_={}
    log_text__=""

def multiprint_(name,texto):
    global log_,log_text__
    print(name,texto)
    #log_[name]=texto
    #print(log_)