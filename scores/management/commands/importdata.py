"""Standalone script that will load data from imdb files into the app db."""

from django.core.management.base import BaseCommand  # CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
from sqlalchemy import create_engine
from io import StringIO
from contextlib import closing
from scores.models import (
    Title,
    Name,
    Principal,
)

import csv
import environ
import pandas as pd

root = environ.Path(__file__) - 3
env = environ.Env()

# set up file paths
TITLE_FILE = 'title.basics.tsv'
NAME_FILE = 'name.basics.tsv'
PRINCIPAL_FILE = 'title.principals.tsv'

# test data
# DATA_PATH = str(root.path('data/test/')) + '/'

# imdb data
DATA_PATH = str(root.path('data/')) + '/'

TITLE_PATH = DATA_PATH + TITLE_FILE
NAME_PATH = DATA_PATH + NAME_FILE
PRINCIPAL_PATH = DATA_PATH + PRINCIPAL_FILE

# create db engine to run sql query generated by functions
ENGINE = create_engine(env('DATABASE_URL'), echo=True)

BAD_NAMES = set(['nm3498919', 'nm3883364', 'nm9220525', 'nm9460234', 'nm3293176', 'nm5585551', 'nm7447340', 'nm3778289', 'nm6843179', 'nm1401713', 'nm9499765', 'nm6634881', 'nm7191052', 'nm8325833', 'nm8903894', 'nm9145233', 'nm9012665', 'nm5381894', 'nm5795147', 'nm5416426', 'nm0788812', 'nm7171926', 'nm5329126', 'nm8614056', 'nm6382803', 'nm5403984', 'nm3317124', 'nm8094915', 'nm4907559', 'nm9511780', 'nm8727319', 'nm6338436', 'nm9436737', 'nm5882033', 'nm8052336', 'nm8135770', 'nm9450335', 'nm2912781', 'nm7714892', 'nm8935775', 'nm7034045', 'nm9565270', 'nm6630721', 'nm7059718', 'nm2610746', 'nm8329298', 'nm9428757', 'nm5825835', 'nm7467576', 'nm0219808', 'nm7323157', 'nm3846046', 'nm9500996', 'nm6250538', 'nm6359191', 'nm7968111', 'nm4081595', 'nm9137477', 'nm7956615', 'nm5137404', 'nm0659653', 'nm8246829', 'nm4432236', 'nm7512466', 'nm5147480', 'nm9388761', 'nm0501516', 'nm8826521', 'nm5970550', 'nm8976897', 'nm9543871', 'nm3466794', 'nm4281755', 'nm6396984', 'nm9609142', 'nm5156383', 'nm9767753', 'nm1737767', 'nm9041076', 'nm6019994', 'nm9626676', 'nm7574477', 'nm8697130', 'nm5480864', 'nm8087043', 'nm7683639', 'nm1110709', 'nm8520502', 'nm4901128', 'nm1951418', 'nm7946364', 'nm8462547', 'nm8190245', 'nm0753833', 'nm8239171', 'nm6948210', 'nm5900676', 'nm8291120', 'nm7613429', 'nm8107486', 'nm7859530', 'nm0874633', 'nm6021545', 'nm2702095', 'nm1622616', 'nm0279170', 'nm1417886', 'nm9362087', 'nm6269571', 'nm8879508', 'nm3597396', 'nm2707745', 'nm6298199', 'nm7975277', 'nm9532978', 'nm1668458', 'nm7727961', 'nm8497449', 'nm8095438', 'nm8009128', 'nm9254127', 'nm6832029', 'nm2626178', 'nm7693251', 'nm7893421', 'nm7706311', 'nm5713989', 'nm8432690', 'nm6024920', 'nm2671441', 'nm7381445', 'nm7315509', 'nm7641386', 'nm7722678', 'nm7389381', 'nm8906263', 'nm8407265', 'nm8871073', 'nm8208125', 'nm5530488', 'nm4484580', 'nm5547892', 'nm2221893', 'nm6367159', 'nm5050998', 'nm3328717', 'nm3589592', 'nm2357338', 'nm9701674', 'nm3393203', 'nm4875999', 'nm8562375', 'nm9182050', 'nm8143080', 'nm9198863', 'nm3802999', 'nm5262222', 'nm5997647', 'nm9257596', 'nm7784161', 'nm9383700', 'nm1690100', 'nm9155866', 'nm9482930', 'nm7901153', 'nm2528531', 'nm9241884', 'nm4928251', 'nm3227290', 'nm6627131', 'nm9588658', 'nm8319896', 'nm1996613', 'nm8270393', 'nm3516280', 'nm5901854', 'nm8097660', 'nm9338750', 'nm6175620', 'nm6129110', 'nm7606208', 'nm2213001', 'nm9073989', 'nm7283087', 'nm7254506', 'nm9111980', 'nm2735501', 'nm1550707', 'nm6102771', 'nm5603834', 'nm1287305', 'nm8233827', 'nm1753649', 'nm4242684', 'nm1632795', 'nm8989242', 'nm6642278', 'nm7636816', 'nm0752741', 'nm3230943', 'nm7801019', 'nm8780358', 'nm9643551', 'nm9570582', 'nm7758260', 'nm3465245', 'nm9507709', 'nm1087761', 'nm1235514', 'nm6566323', 'nm3928617', 'nm8873339', 'nm5971804', 'nm0383037', 'nm1233121', 'nm4780290', 'nm4269577', 'nm2174180', 'nm5557064', 'nm2884782', 'nm8614410', 'nm2075629', 'nm9530580', 'nm7183931', 'nm9511777', 'nm3717019', 'nm6003839', 'nm9391377', 'nm8271016', 'nm9490889', 'nm0640681', 'nm8569633', 'nm3878857', 'nm9495378', 'nm6302337', 'nm8328381', 'nm9657900', 'nm9162375', 'nm9088554', 'nm0734078', 'nm7770878', 'nm6730740', 'nm7682773', 'nm6177438', 'nm9769121', 'nm4940181', 'nm8440581', 'nm4972572', 'nm1777254', 'nm9570605', 'nm4924070', 'nm0659559', 'nm6790188', 'nm7967053', 'nm6951194', 'nm1653529', 'nm8579868', 'nm4681514', 'nm9038726', 'nm6012474', 'nm5281936', 'nm6312764', 'nm9022100', 'nm7664488', 'nm8363294', 'nm8172220', 'nm4770424', 'nm3127685', 'nm5606303', 'nm8114636', 'nm7058741', 'nm2021406', 'nm5778698', 'nm5267293', 'nm4443816', 'nm9347527', 'nm8329761', 'nm5735527', 'nm1512281', 'nm2715758', 'nm8004064', 'nm2107388', 'nm8795665', 'nm1212088', 'nm5434082', 'nm8702101', 'nm7828285', 'nm7330323', 'nm0552908', 'nm5401436', 'nm5751142', 'nm6776583', 'nm1779641', 'nm9336322', 'nm9064757', 'nm8476512', 'nm1965173', 'nm3799416', 'nm5467914', 'nm7825205', 'nm3528112', 'nm7227873', 'nm8657533', 'nm7658762', 'nm3869875', 'nm9137444', 'nm2734387', 'nm6164684', 'nm1852044', 'nm0735722', 'nm8594922', 'nm9549533', 'nm5928126', 'nm8121679', 'nm3248222', 'nm6844650', 'nm7965435', 'nm4345758', 'nm6725003', 'nm7495854', 'nm3757576', 'nm5477834', 'nm5770153', 'nm3879875', 'nm7258954', 'nm8474737', 'nm5501760', 'nm3067464', 'nm2901410', 'nm3977187', 'nm7958041', 'nm9615036', 'nm9514204', 'nm7748063', 'nm8893355', 'nm1883079', 'nm3817030', 'nm7817297', 'nm3821675', 'nm9437633', 'nm7839521', 'nm6643606', 'nm9332128', 'nm9636476', 'nm7182502', 'nm9472912', 'nm3740378', 'nm8229778', 'nm7075972', 'nm8803548', 'nm4743295', 'nm4425822', 'nm1270630', 'nm7052043', 'nm8847511', 'nm3721442', 'nm4997444', 'nm8952185', 'nm1695787', 'nm6919525', 'nm4497120', 'nm8754814', 'nm7104511', 'nm8547435', 'nm8783336', 'nm4430517', 'nm5170823', 'nm7531999', 'nm7020029', 'nm7934724', 'nm9576441', 'nm8218403', 'nm4487064', 'nm5218029', 'nm5183032', 'nm9573728', 'nm7963210', 'nm6634723', 'nm7301077', 'nm5188171', 'nm7497421', 'nm7907984', 'nm4088181', 'nm9466046', 'nm8052248', 'nm5678529', 'nm2571139', 'nm2037285', 'nm1034200', 'nm4384156', 'nm8895303', 'nm6954092', 'nm8207905', 'nm8499788', 'nm6924312', 'nm7292697', 'nm6169373', 'nm9461547', 'nm3244099', 'nm2147416', 'nm3807831', 'nm9629808', 'nm6188219', 'nm3335515', 'nm8377982', 'nm5360314', 'nm8985429', 'nm8830379', 'nm6901444', 'nm8352260', 'nm9364917', 'nm2409353', 'nm3445364', 'nm0294787', 'nm7480410', 'nm1001709', 'nm9080785', 'nm1821809', 'nm3341416', 'nm1989036', 'nm8316100', 'nm1623778', 'nm4024027', 'nm2587837', 'nm8556075', 'nm1784748', 'nm2396567', 'nm8869476', 'nm6355454', 'nm5814024', 'nm4957699', 'nm7060878', 'nm8052247', 'nm6092119', 'nm8697404', 'nm9372530', 'nm5478515', 'nm3641806', 'nm5261987', 'nm2079433', 'nm6010885', 'nm8377082', 'nm6432961', 'nm7439562', 'nm1026618', 'nm5030319', 'nm4117296', 'nm7259907', 'nm9120419', 'nm8800409', 'nm7570926', 'nm8194084', 'nm6544751', 'nm9190574', 'nm9632081', 'nm8518997', 'nm3264686', 'nm8319393', 'nm6346522', 'nm7963682', 'nm7676870', 'nm0484138', 'nm9354135', 'nm7256576', 'nm7449393', 'nm1856649', 'nm7087829', 'nm9259514', 'nm8431195', 'nm6759154', 'nm7032456', 'nm8577231', 'nm9271255', 'nm8542446', 'nm4438462', 'nm3388982', 'nm2014212', 'nm8628665', 'nm2687361', 'nm9243688', 'nm9433087', 'nm5529380', 'nm6489376', 'nm9410592', 'nm5252203', 'nm5881058', 'nm8699111', 'nm4715476', 'nm4477428', 'nm2886150', 'nm2665465', 'nm0687496', 'nm5865373', 'nm7504406', 'nm5116724', 'nm8270407', 'nm9159332', 'nm0181980', 'nm4063368', 'nm8119815', 'nm9522976', 'nm9345798', 'nm8643783', 'nm8096051', 'nm9036075', 'nm9228651', 'nm3200888', 'nm8524284', 'nm6940725', 'nm5890198', 'nm6003780', 'nm4804834', 'nm5334098', 'nm3925501', 'nm6918610', 'nm2299443', 'nm2552505', 'nm6960525', 'nm8993294', 'nm9737370', 'nm6395567', 'nm9105813', 'nm8551842', 'nm0402378', 'nm3094547', 'nm9494502', 'nm3478300', 'nm3223322', 'nm7974525', 'nm7671885', 'nm4390271', 'nm2125997', 'nm5743597', 'nm9366097', 'nm9179918', 'nm6100950', 'nm5978936', 'nm2600840', 'nm4086322', 'nm7193051', 'nm1155698', 'nm8847544', 'nm9055910', 'nm7626847', 'nm4293967', 'nm8702395', 'nm4415154', 'nm5456513', 'nm9387241', 'nm7704689', 'nm5813282', 'nm4865372', 'nm7441342', 'nm9313869', 'nm3764075', 'nm5937168', 'nm6388719', 'nm9112104', 'nm7735327', 'nm7392676', 'nm4992856', 'nm2089512', 'nm8368395', 'nm9111010', 'nm8541997', 'nm7883702', 'nm7922488', 'nm6966976', 'nm5711759', 'nm9615032', 'nm1886313', 'nm7907599', 'nm8439797', 'nm9640719', 'nm1169634', 'nm6192773', 'nm2700599', 'nm6753446', 'nm4230038', 'nm9363743', 'nm9517860', 'nm5341770', 'nm8057846', 'nm9036367', 'nm0123871', 'nm9408390', 'nm8053946', 'nm4932754', 'nm8639413', 'nm6723485', 'nm7050767', 'nm7601648', 'nm9296606', 'nm6489052', 'nm9128911', 'nm8947198', 'nm0030281', 'nm6554023', 'nm9553333', 'nm4553963', 'nm7785681', 'nm7792589', 'nm8843497', 'nm7365710', 'nm4983820', 'nm3454019', 'nm0384739', 'nm6269406', 'nm8804280', 'nm9421040', 'nm9216022', 'nm5080096', 'nm6491379', 'nm7971378', 'nm7157721', 'nm0543071', 'nm0248490', 'nm7286060', 'nm8609724', 'nm8835127', 'nm4366431', 'nm1779352', 'nm7783177', 'nm9551719', 'nm4958268', 'nm9439850', 'nm6954350', 'nm9381501', 'nm2005088', 'nm2165109', 'nm3761543', 'nm8478729', 'nm6515131', 'nm4623971', 'nm4748943', 'nm6738071', 'nm6977960', 'nm4708952', 'nm7641602', 'nm8817501', 'nm0043365', 'nm4104787', 'nm8790824', 'nm2114706', 'nm2282189', 'nm3070740', 'nm5253651', 'nm0874955', 'nm4852231', 'nm6267165', 'nm0249600', 'nm8752117', 'nm5645897', 'nm0624432', 'nm8248947', 'nm9064694', 'nm9080130', 'nm0206222', 'nm9455247', 'nm1686562', 'nm9430232', 'nm6377950', 'nm6383177', 'nm4602152', 'nm7823945', 'nm9527637', 'nm2255424', 'nm6175810', 'nm8449135', 'nm8769545', 'nm9658164', 'nm8632200', 'nm4251863', 'nm8835733', 'nm9011084', 'nm9029856', 'nm2118078', 'nm7365525', 'nm4652502', 'nm8371693', 'nm0839793', 'nm9166296', 'nm4563299', 'nm9618907', 'nm7549865', 'nm7614088', 'nm8938702', 'nm6980994', 'nm5560260', 'nm9381612', 'nm6962229', 'nm5650280', 'nm6398503', 'nm9442098', 'nm7417789', 'nm7619673', 'nm4619658', 'nm3778982', 'nm6270141', 'nm3064095', 'nm0251818', 'nm1443345', 'nm0498259', 'nm6085505', 'nm2882991', 'nm6664141', 'nm8352590', 'nm8541294', 'nm9352055', 'nm8806265', 'nm6344661', 'nm5778458', 'nm9319494', 'nm1387716', 'nm6224598', 'nm8428069', 'nm0503085', 'nm7389226', 'nm4114409', 'nm1651414', 'nm7783179', 'nm4128522', 'nm3067812', 'nm5058859', 'nm6600956', 'nm8506000', 'nm7816969', 'nm6416269', 'nm9513667', 'nm9016151', 'nm6505281', 'nm4002341', 'nm4597984', 'nm7402827', 'nm5472999', 'nm4048518', 'nm7013477', 'nm8120081', 'nm7327319', 'nm8291750', 'nm7057345', 'nm8725793', 'nm8159955', 'nm9526357', 'nm7422811', 'nm6092576', 'nm4026741', 'nm8601550', 'nm8484473', 'nm1537340', 'nm7706880', 'nm9516906', 'nm8412435', 'nm8577697', 'nm8685862', 'nm9230061', 'nm2836656', 'nm5847940', 'nm5794004', 'nm6050994', 'nm9149649', 'nm5879739', 'nm2576656', 'nm3683296', 'nm8900735', 'nm5041935', 'nm9546991', 'nm7446999', 'nm7660195', 'nm5764509', 'nm9152617', 'nm5796316', 'nm5977147', 'nm9396158', 'nm4474874', 'nm5684544', 'nm7144088', 'nm4737768', 'nm9437825', 'nm7820948', 'nm9330670', 'nm7714238', 'nm8244698', 'nm7984868', 'nm9021363', 'nm6250452', 'nm9581943', 'nm4864462', 'nm8423951', 'nm7280957', 'nm3123677', 'nm5668762', 'nm9745456', 'nm5083490', 'nm4797071', 'nm0662054', 'nm7940686', 'nm4886795', 'nm1201377', 'nm9485711', 'nm8769544', 'nm5862387', 'nm5697936', 'nm5277626', 'nm2792700', 'nm5796805', 'nm3869263', 'nm9401587', 'nm7970777', 'nm8599936', 'nm7906966', 'nm8922295', 'nm2879298', 'nm4658371', 'nm7333886', 'nm7629839', 'nm9006813', 'nm8836066', 'nm5595845', 'nm3148453', 'nm8199011', 'nm7264520', 'nm5729869', 'nm5327840', 'nm8788583', 'nm2649184', 'nm7901502', 'nm8989689', 'nm9188965', 'nm1777321', 'nm6516433', 'nm9540998', 'nm5689020', 'nm1361961', 'nm5022603', 'nm5732322', 'nm9372952', 'nm9315442', 'nm7966832', 'nm9316963', 'nm3789603', 'nm9499289', 'nm4249863', 'nm6798604', 'nm9430357', 'nm7717821', 'nm9137443', 'nm1711799', 'nm2450439', 'nm6416268', 'nm4207809', 'nm9760654', 'nm7522666', 'nm4407965', 'nm3127152', 'nm9169043', 'nm9639304', 'nm1069279', 'nm1975423', 'nm0482877', 'nm8724094', 'nm5968437', 'nm8085352', 'nm2520981', 'nm5061153', 'nm2815635', 'nm9342307', 'nm0623375', 'nm4775019', 'nm6998011', 'nm1664628', 'nm9014765', 'nm3645038', 'nm5298806', 'nm2519261', 'nm4154193', 'nm1696240', 'nm9498796', 'nm2698031', 'nm9638326', 'nm9532979', 'nm2370872', 'nm0316631', 'nm9594425', 'nm8873259', 'nm9357822', 'nm8760323', 'nm9690828', 'nm6607030', 'nm9536423', 'nm4508866', 'nm8781425', 'nm1645548', 'nm1840657', 'nm8767125', 'nm8817265', 'nm5823168', 'nm8209052', 'nm2511656', 'nm6247067', 'nm8670068', 'nm1697772', 'nm9454310', 'nm5154178', 'nm1822727', 'nm7798473', 'nm8357611', 'nm4144494', 'nm7269724', 'nm3079037', 'nm8901185', 'nm4948436', 'nm8055083', 'nm8198304', 'nm0645926', 'nm3935597', 'nm9609252', 'nm7324082', 'nm3521350', 'nm3826861', 'nm5603215', 'nm7700311', 'nm9502587', 'nm6398337', 'nm9562988', 'nm4785289', 'nm9428974', 'nm6276600', 'nm0873289', 'nm9360822', 'nm2517598', 'nm8476513', 'nm2695452', 'nm0319466', 'nm9559322', 'nm7848956', 'nm3581621', 'nm3120697', 'nm7107451', 'nm9108520', 'nm5549331', 'nm8258541', 'nm4419794', 'nm8284381', 'nm4900573', 'nm2106974', 'nm8766498', 'nm1757575', 'nm4512852', 'nm5859373', 'nm1757567', 'nm5133735', 'nm7909479', 'nm6139116', 'nm9577223', 'nm9595024', 'nm8376124', 'nm3394484', 'nm5168993', 'nm8962936', 'nm4392799', 'nm9391618', 'nm1813490', 'nm1922784', 'nm8300005', 'nm1292327', 'nm6740045', 'nm9564930', 'nm9253020', 'nm9585944', 'nm8430812', 'nm2794883', 'nm3309533', 'nm9499766', 'nm6796710', 'nm8304716', 'nm7963569', 'nm8661510', 'nm8410933', 'nm2530639', 'nm1280367', 'nm9519832', 'nm6224735', 'nm7565016', 'nm0155303', 'nm8745957', 'nm1313625', 'nm0624101', 'nm6982700', 'nm8979723', 'nm9128854', 'nm1683237', 'nm7706740', 'nm9073004', 'nm8110068', 'nm0833648', 'nm6794806', 'nm9350433', 'nm3720296', 'nm1885633', 'nm6818628', 'nm5404654', 'nm6424236', 'nm4598874', 'nm8258202', 'nm0944395', 'nm8894150', 'nm9142306', 'nm8607963', 'nm9475098', 'nm4179816', 'nm8731377', 'nm8641496', 'nm6815377', 'nm9525164', 'nm4198470', 'nm9603229', 'nm6547183', 'nm9174685', 'nm3702868', 'nm6090743', 'nm0600636', 'nm5392929', 'nm7672340', 'nm8737604', 'nm0507510', 'nm5843882', 'nm9084952', 'nm6132153', 'nm7672341', 'nm8191088', 'nm9098626', 'nm5357855', 'nm8030349', 'nm4361716', 'nm8385329', 'nm9469077', 'nm7928064', 'nm6860821', 'nm9662012', 'nm4629799', 'nm9568149', 'nm9745968', 'nm8904063', 'nm4071814', 'nm8801559', 'nm6412448', 'nm5198268', 'nm7053793', 'nm8944610', 'nm9564763', 'nm7098971', 'nm8652755', 'nm3094036', 'nm1802584', 'nm6227699', 'nm1281620', 'nm6672271', 'nm2181179', 'nm7898714', 'nm4205519', 'nm7219371', 'nm4869680', 'nm1930387', 'nm9474030', 'nm7652942', 'nm1579870', 'nm8245955', 'nm8007211', 'nm1298621', 'nm5518175', 'nm6609829', 'nm2010754', 'nm7797278', 'nm1123541', 'nm9043473', 'nm7467854', 'nm9519235', 'nm8894351', 'nm3288398', 'nm0717351', 'nm7709293', 'nm4891011', 'nm6542892', 'nm6854332', 'nm9427277', 'nm8953141', 'nm1540828', 'nm7636562', 'nm3879757', 'nm9165795', 'nm3794520', 'nm7433447', 'nm7860096', 'nm7748296', 'nm9024876', 'nm9313589', 'nm1515461', 'nm9595756', 'nm7483424', 'nm2368341', 'nm9518710', 'nm8578981', 'nm1423714', 'nm5796498', 'nm7682772', 'nm9247093', 'nm4624521', 'nm4276297', 'nm2591646', 'nm4386074', 'nm5471292', 'nm9738948', 'nm5089808', 'nm9112103', 'nm3938264', 'nm7432630', 'nm5868221', 'nm3233432', 'nm5046982', 'nm9368555', 'nm8284355', 'nm9488409', 'nm3124182', 'nm9369622', 'nm9527030', 'nm0078881', 'nm9181942', 'nm4270201', 'nm7165251', 'nm6406468', 'nm7575836', 'nm9098742', 'nm5994629', 'nm9332136', 'nm8302948', 'nm5338343', 'nm8377117', 'nm8279934', 'nm5658229', 'nm7519962', 'nm9689585', 'nm8935770', 'nm7822700', 'nm6482376', 'nm7826766', 'nm9551711', 'nm7557496', 'nm0316210', 'nm7244032', 'nm8324788', 'nm7955272', 'nm8110436', 'nm4369446', 'nm8840145', 'nm7752724', 'nm9532629', 'nm2781055', 'nm0188052', 'nm2944757', 'nm5720159', 'nm9380516', 'nm9133023', 'nm4587110', 'nm4344506', 'nm4788174', 'nm4876692', 'nm0823243', 'nm9169449', 'nm9395503', 'nm9561972', 'nm8562374', 'nm1342476', 'nm2179974', 'nm7283086', 'nm5514751', 'nm9410042', 'nm5252007', 'nm8604461', 'nm8798617', 'nm9583107', 'nm9687107', 'nm6362467', 'nm7672342', 'nm7495838', 'nm6424678', 'nm7585678', 'nm9541444', 'nm0903635', 'nm8498855', 'nm3131389', 'nm5333413', 'nm9258449', 'nm9531802', 'nm3760735', 'nm8833782', 'nm7826219', 'nm4395417', 'nm7970743', 'nm9654859', 'nm8093339', 'nm6630962', 'nm8928466', 'nm0162284', 'nm7076144', 'nm4644735', 'nm9195746', 'nm4196188', 'nm3888240', 'nm8631342', 'nm9508171', 'nm5577436', 'nm0204040', 'nm6649554', 'nm9638354', 'nm9382723', 'nm9574383', 'nm1252044', 'nm4661025', 'nm4658309', 'nm4589105', 'nm3934694', 'nm9137645', 'nm6776957', 'nm1275349', 'nm1830201', 'nm3151343', 'nm7465538', 'nm8185571', 'nm6548588', 'nm2196328', 'nm9480028', 'nm9441815', 'nm8360931', 'nm8320031', 'nm8815059', 'nm8198336', 'nm3924824', 'nm9478625', 'nm1685176', 'nm2974980', 'nm6160696', 'nm4008630', 'nm8825900', 'nm0380120', 'nm5276715', 'nm1278029', 'nm0890904', 'nm7388846', 'nm2354207', 'nm4673800', 'nm9049182', 'nm9347561', 'nm9214093', 'nm8488919', 'nm8103172', 'nm8736449', 'nm6918430', 'nm9070053', 'nm3822228', 'nm7432208', 'nm6867621', 'nm1813208', 'nm9515137', 'nm1524552', 'nm5679096', 'nm6342187', 'nm8329301', 'nm5742810', 'nm8211815', 'nm9453801', 'nm8847490', 'nm4768810', 'nm2173975', 'nm9057179', 'nm0040196', 'nm9056027', 'nm8304593', 'nm1696887', 'nm6370952', 'nm3148450', 'nm6839666', 'nm5091152', 'nm7215425', 'nm1056872', 'nm8857992', 'nm4272901', 'nm1651458', 'nm9099161', 'nm8748649', 'nm7360586', 'nm7403661', 'nm8801739', 'nm7240436', 'nm1317385', 'nm9401539', 'nm9554933', 'nm4751126', 'nm9623288', 'nm3082205', 'nm9561248', 'nm9340985', 'nm8078803', 'nm7987429', 'nm6202598', 'nm1771866', 'nm9615033', 'nm7305766', 'nm9380482', 'nm2309748', 'nm1510030', 'nm9605808', 'nm8490986', 'nm4811937', 'nm8442256', 'nm1085179', 'nm2809403', 'nm8284363', 'nm9604224', 'nm7335460', 'nm4183449', 'nm6998850', 'nm9277875', 'nm0093211', 'nm6458525', 'nm2159189', 'nm9059676', 'nm7694390', 'nm6311386', 'nm8835436', 'nm2382509', 'nm7793077', 'nm8585524', 'nm7606084', 'nm5662269', 'nm7432220', 'nm1792722', 'nm6911182', 'nm9350748', 'nm5060396', 'nm0421962', 'nm6497302', 'nm8139945', 'nm4661242', 'nm9353813', 'nm3776663', 'nm4363997', 'nm4812930', 'nm9559462', 'nm0678441', 'nm6491097', 'nm9412621', 'nm9550980', 'nm5405937', 'nm9466347', 'nm5016760', 'nm3655798', 'nm1895202', 'nm6482585', 'nm9412186', 'nm9011730', 'nm9126996', 'nm9436617', 'nm1028808', 'nm8383133', 'nm7710961', 'nm3798114', 'nm3369181', 'nm9769127', 'nm6428813', 'nm1813092', 'nm2028372', 'nm9161033', 'nm9662362', 'nm8814871', 'nm3597914', 'nm9528060', 'nm5516263', 'nm5755775', 'nm9532567', 'nm6706647', 'nm1447609', 'nm4656106', 'nm5639893', 'nm1832211', 'nm9137507', 'nm9120775', 'nm5165563', 'nm1840977', 'nm0558488', 'nm9417854', 'nm3516645', 'nm1741060', 'nm8450257', 'nm2115903', 'nm9544034', 'nm0557966', 'nm8842395', 'nm4993248', 'nm4808949', 'nm4329232', 'nm8683027', 'nm1267046', 'nm2993990', 'nm8877235', 'nm9445638', 'nm7061687', 'nm9599922', 'nm0306321', 'nm8572477', 'nm5682152', 'nm9277133', 'nm9159249', 'nm4917988', 'nm9519020', 'nm7818020', 'nm6890001', 'nm8938183', 'nm0733402', 'nm8955204', 'nm8546299', 'nm9337303', 'nm7998144', 'nm8625031', 'nm7278526', 'nm5842792', 'nm3606428', 'nm0482886', 'nm6016831', 'nm9726859', 'nm0853273', 'nm2394195', 'nm3510277', 'nm6699386', 'nm3620663'])
BAD_TITLES = set(['tt7716230', 'tt6371876', 'tt7764206', 'tt7716048', 'tt7716054', 'tt6029720', 'tt5135404', 'tt5684254', 'tt4786290', 'tt6030010', 'tt6659424', 'tt7890420', 'tt6485322', 'tt7107418', 'tt5796140', 'tt0258245', 'tt7716078', 'tt4734100', 'tt6798666', 'tt7093314', 'tt7332192', 'tt7422622', 'tt6354302', 'tt7893404', 'tt6471200', 'tt7235264', 'tt0167231', 'tt7117958', 'tt6967202', 'tt7269970'])


def load_titles():
    """Read title.basics.tsv into db."""
    print('loading titles')
    Title.objects.all().delete()

    # create dataframe
    df = pd.read_csv(
        TITLE_PATH,
        sep='\t',
        header=0,
        names=[
            'id',
            'title_type',
            'primary_title',
            'original_title',
            'is_adult',
            'start_year',
            'end_year',
            'runtime_minutes',
            'genres'
        ],
        quoting=3,
        na_values=['\\N']
    )

    df = df.drop(columns=['original_title', 'runtime_minutes'])
    df['is_adult'] = df['is_adult'].map({0: False, 1: True})

    df.to_sql(Title._meta.db_table, ENGINE, if_exists='append', index=False)

    return None


def load_names():
    """Read name.basics.tsv into db."""
    print('loading names')

    # drop all records from table
    Name.objects.all().delete()

    df = pd.read_csv(
        NAME_PATH,
        sep='\t',
        header=0,
        names=[
            'id',
            'primary_name',
            'birth_year',
            'death_year',
            'professions',
            'known_for'
        ],
        quoting=3,
        na_values=['\\N'],
    )
    df['lowercase_name'] = df['primary_name'].apply(lambda x: x.lower())
    df['in_graph'] = False

    df.to_sql(Name._meta.db_table, ENGINE, if_exists='append', index=False)


def load_principals():
    """
    Read title.principals.tsv into db.

    principalCast is given as an array of comma-separated strings.
    This splits the array so that one row turns into multiple rows
    for insertion into the join table.
    """
    print('loading principals')
    # delete all records from table
    Principal.objects.all().delete()

    # create dataframe
    df = pd.read_csv(
        PRINCIPAL_PATH,
        sep='\t',
        header=0,
        names=[
            'title_id',
            'ordering',
            'name_id',
            'category',
            'job',
            'characters'
        ],
        quoting=3,
        na_values=['\\N']
    )

    df = df.drop(columns=['ordering', 'category', 'job', 'characters'])

    # uncomment this section if you need to update BAD_NAMES and BAD_TITLES
    # (takes ~ 24 hrs)
    # bad_titles = set()
    # bad_names = set()
    # for row in df.itertuples():
    #     name = row[2]
    #     title = row[1]
    #     print(row[0])

    #     try:
    #         Title.objects.get(id=title)
    #         pass
    #     except ObjectDoesNotExist:
    #         bad_titles.add(title)

    #     try:
    #         Name.objects.get(id=name)
    #         pass
    #     except ObjectDoesNotExist:
    #         bad_names.add(name)

    # print('=== TITLES ===')
    # print(bad_titles)
    # print('=== NAMES ===')
    # print(bad_names)
    # return

    # specify order of columns
    df = df[['name_id', 'title_id']]

    # rename index to id to match table
    df.index.names = ['id']
    print(df)

    sio = StringIO()
    writer = csv.writer(sio, delimiter='\t')

    for row in df.itertuples():
        name_id = row[1]
        title_id = row[2]

        if((name_id not in BAD_NAMES) and (title_id not in BAD_TITLES)):
            writer.writerow([row[0], name_id, title_id])

    sio.seek(0)

    print('written')
    with closing(connection.cursor()) as cursor:
        cursor.copy_from(
            file=sio,
            table='scores_principal',
            sep='\t',
            columns=('id, name_id', 'title_id')
        )


class Command(BaseCommand):
    """Add command line function to load data when calling manage.py."""

    help = 'Reads IMDB data files into the database'

    def add_arguments(self, parser):
        """Add arg to specify file type (or all) to load into db."""
        parser.add_argument(
            'file',
            help='file to add: titles, names, principals, or all'
        )

    def handle(self, *args, **options):
        """Load all imdb data."""
        data = options['file']

        if data == 'titles' or data == 't':
            load_titles()
        elif data == 'names' or data == 'n':
            load_names()
        elif data == 'principals' or data == 'p':
            load_principals()
        elif data == 'all':
            load_titles()
            load_names()
            load_principals()
