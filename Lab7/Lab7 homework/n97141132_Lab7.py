
import numpy as np
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

# 讀取原始資料
data = np.loadtxt(
    "Bank_Customer.csv",
    skiprows=1,
    dtype=str,
    delimiter=","
)

# 原始欄位：
# customer_id, credit_score, country, gender, age,
# tenure, balance, products_number, credit_card,
# active_member, estimated_salary, churn

# 1. 移除沒有意義的 customer_id
data = data[:, 1:]

# 2. 將 country 轉換為數值 (One-Hot Encoding)
country = data[:, 1]

countries = np.unique(country)
country_encoded = np.zeros((len(country), len(countries)))

for i in range(len(countries)):
    country_encoded[:, i] = (country == countries[i]).astype(float)

# 3. 將 gender 轉換為數值
gender = data[:, 2]
gender_encoded = (gender == "Male").astype(float).reshape(-1, 1)

# 4. 取出其他數值特徵
# 移除 country 和 gender 欄位，最後一欄 churn 是標籤
numeric_features = data[:, [0, 3, 4, 5, 6, 7, 8, 9]].astype(float)

# 5. 合併數值特徵
X = np.hstack((
    numeric_features,
    country_encoded,
    gender_encoded
))

# 6. 取出預測標籤 churn
y = data[:, -1].astype(int)

# 7. 切割 Training data 與 Testing data
x_train, x_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.3,
    random_state=42,
    stratify=y
)

# 8. 標準化特徵
# 只使用訓練集計算平均值與標準差
scaler = StandardScaler()
x_train = scaler.fit_transform(x_train)
x_test = scaler.transform(x_test)

# 9. 將前處理後的完整資料儲存成 CSV
# 為了保持與訓練／測試流程一致，這裡使用
# 訓練集建立的 scaler 轉換全部資料
X_scaled = scaler.transform(X)
pre_data = np.column_stack((X_scaled, y))

np.savetxt(
    "Bank_Customer_Preprocessed.csv",
    pre_data,
    delimiter=","
)

# 10. 建立 Logistic Regression 分類器
clf = LogisticRegression(max_iter=1000)

# 使用訓練集訓練
clf.fit(x_train, y_train)

# 使用測試集預測
pred = clf.predict(x_test)

# 11. 輸出預測準確率
print(str(accuracy_score(pred, y_test) * 100) + "%")
