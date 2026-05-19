from sklearn.linear_model import LinearRegression

x = [50,100,150,200]
y= [20.935, 44.0150, 66.78, 89.092]
std = [0.097136637, 0.14550728, 0.245120808, 0.34869803]
wi = [1/s**2 for s in std]
model = LinearRegression()
model.fit([[i] for i in x], y, sample_weight=wi)
print( model.coef_)
print(model.intercept_)

model.fit([[i] for i in x], y)
print( model.coef_)
print(model.intercept_)