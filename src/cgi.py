"""Forward conditional graph innovation; no structural causal interpretation."""
import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
BASE=['lag1','lag7','lag6','lag30','shock','downside','slot','density','density_change']
GRAPH=['gae','joint','joint_std','joint_change','joint_roll5']
def ridge(alpha=10.):return make_pipeline(StandardScaler(),Ridge(alpha=alpha))
def features(u,x,mean,scale):
    state=np.clip((x[:,[0,4]]-mean)/scale,-3,3)
    return np.concatenate([u,u*state[:,:1],u*state[:,1:]],axis=1)
class CGI:
    def __init__(self,alpha=10.,orthogonal=True):self.alpha=alpha;self.orthogonal=orthogonal
    def fit(self,f):
        x=f[BASE].to_numpy();z=f[GRAPH].to_numpy();y=f.target.to_numpy();years=f.index.year
        residuals=[];innovations=[];states=[];self.fold_audit=[]
        for year in sorted(set(years))[1:]:
            a=years<year;b=years==year
            if a.sum()<100 or b.sum()<30:continue
            if f.target_time[a].max()>=f.index[b].min():raise ValueError('forward label overlap')
            base=ridge(self.alpha).fit(x[a],y[a]);nuisance=ridge(self.alpha).fit(x[a],z[a])
            residuals.append(y[b]-base.predict(x[b]));innovations.append(z[b]-nuisance.predict(x[b]) if self.orthogonal else z[b]);states.append(x[b])
            self.fold_audit.append({'validation_year':int(year),'training_max':str(f.index[a].max()),'label_max':str(f.target_time[a].max())})
        if not residuals:raise ValueError('At least two years required')
        xx=np.concatenate(states);uu=np.concatenate(innovations)
        self.mean=xx[:,[0,4]].mean(0);self.scale=np.maximum(xx[:,[0,4]].std(0),1e-8)
        self.correction=ridge(self.alpha).fit(features(uu,xx,self.mean,self.scale),np.concatenate(residuals))
        self.base=ridge(self.alpha).fit(x,y);self.nuisance=ridge(self.alpha).fit(x,z);return self
    def predict_components(self,f):
        x=f[BASE].to_numpy();z=f[GRAPH].to_numpy();u=z-self.nuisance.predict(x) if self.orthogonal else z
        return self.base.predict(x),self.correction.predict(features(u,x,self.mean,self.scale))
    def predict(self,f,weight=1.):
        b,c=self.predict_components(f);return b+weight*c
